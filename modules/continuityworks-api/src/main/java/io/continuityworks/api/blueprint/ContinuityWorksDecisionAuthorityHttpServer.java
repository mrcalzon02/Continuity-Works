package io.continuityworks.api.blueprint;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executor;

/**
 * Minimal authoritative HTTP transport for {@link ContinuityWorksDecisionAuthorityAdapter}.
 *
 * <p>The listener owns only serialization, request/session revision checks and HTTP status mapping.
 * Decision vocabulary, dependency semantics, candidate legality, validation and finalization remain
 * delegated to the configured Continuity Works API through {@code ContinuityWorksDecisionAuthorityAdapter}.</p>
 *
 * <p>This service is intended to sit behind the existing delegated Python publication bridge or
 * an equivalent local companion-mod transport. It does not expose raw world mutation operations.</p>
 */
public final class ContinuityWorksDecisionAuthorityHttpServer implements AutoCloseable {
    public static final String ROUTE_PREFIX = "/v1/blueprints/decision";
    public static final int DEFAULT_MAX_BODY_BYTES = 64 * 1024;

    private final ContinuityWorksDecisionAuthorityAdapter authority;
    private final BlueprintDecisionCandidateSource candidateSource;
    private final HttpServer server;
    private final int maxBodyBytes;
    private final ConcurrentHashMap<UUID, BlueprintDecisionChain.State> sessions = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<UUID, BlueprintRequest> requests = new ConcurrentHashMap<>();

    public ContinuityWorksDecisionAuthorityHttpServer(
        ContinuityWorksCompactBlueprintApi api,
        InetSocketAddress address
    ) throws IOException {
        this(new ContinuityWorksDecisionAuthorityAdapter(api), null, address, DEFAULT_MAX_BODY_BYTES, null);
    }

    public ContinuityWorksDecisionAuthorityHttpServer(
        ContinuityWorksCompactBlueprintApi api,
        BlueprintDecisionCandidateSource candidateSource,
        InetSocketAddress address
    ) throws IOException {
        this(new ContinuityWorksDecisionAuthorityAdapter(api), candidateSource, address, DEFAULT_MAX_BODY_BYTES, null);
    }

    public ContinuityWorksDecisionAuthorityHttpServer(
        ContinuityWorksDecisionAuthorityAdapter authority,
        InetSocketAddress address,
        int maxBodyBytes,
        Executor executor
    ) throws IOException {
        this(authority, null, address, maxBodyBytes, executor);
    }

    public ContinuityWorksDecisionAuthorityHttpServer(
        ContinuityWorksDecisionAuthorityAdapter authority,
        BlueprintDecisionCandidateSource candidateSource,
        InetSocketAddress address,
        int maxBodyBytes,
        Executor executor
    ) throws IOException {
        this.authority = Objects.requireNonNull(authority, "authority");
        this.candidateSource = candidateSource;
        Objects.requireNonNull(address, "address");
        if (maxBodyBytes < 1) throw new IllegalArgumentException("maxBodyBytes must be positive");
        this.maxBodyBytes = maxBodyBytes;
        this.server = HttpServer.create(address, 0);
        if (executor != null) this.server.setExecutor(executor);
        this.server.createContext("/", this::handle);
    }

    public void start() {
        server.start();
    }

    public InetSocketAddress address() {
        return server.getAddress();
    }

    public int activeDecisionCount() {
        return sessions.size();
    }

    public boolean dynamicCandidateSourceConfigured() {
        return candidateSource != null;
    }

    public void restoreDecision(BlueprintDecisionChain.State state) {
        Objects.requireNonNull(state, "state");
        BlueprintDecisionChain.State existing = sessions.putIfAbsent(state.requestId(), state);
        if (existing != null && !existing.equals(state)) {
            throw new IllegalStateException("decision request already has different authoritative state: " + state.requestId());
        }
    }

    /** Restore request context and state together so dynamic candidate discovery can resume safely. */
    public void restoreDecision(BlueprintRequest request, BlueprintDecisionChain.State state) {
        Objects.requireNonNull(request, "request");
        Objects.requireNonNull(state, "state");
        if (!request.requestId().equals(state.requestId())) {
            throw new IllegalArgumentException("request and decision state requestId must match");
        }
        restoreDecision(state);
        BlueprintRequest existing = requests.putIfAbsent(request.requestId(), request);
        if (existing != null && !existing.equals(request)) {
            throw new IllegalStateException("decision request already has different authoritative request context: " + request.requestId());
        }
    }

    public void forgetDecision(UUID requestId) {
        UUID id = Objects.requireNonNull(requestId, "requestId");
        sessions.remove(id);
        requests.remove(id);
    }

    @Override
    public void close() {
        server.stop(0);
        sessions.clear();
        requests.clear();
    }

    private void handle(HttpExchange exchange) throws IOException {
        try {
            String method = exchange.getRequestMethod().toUpperCase();
            String path = exchange.getRequestURI().getPath();
            if ("GET".equals(method) && "/v1/health".equals(path)) {
                send(exchange, 200, Map.of(
                    "ok", true,
                    "service", "continuity-works-decision-authority",
                    "apiVersion", authority.apiVersion().toString(),
                    "protocolVersion", authority.decisionProfile().protocolVersion(),
                    "activeDecisions", activeDecisionCount(),
                    "dynamicCandidateSourceConfigured", dynamicCandidateSourceConfigured()
                ));
                return;
            }
            if ("GET".equals(method) && (ROUTE_PREFIX + "/profile").equals(path)) {
                send(exchange, 200, profileDocument());
                return;
            }
            if (!path.startsWith(ROUTE_PREFIX + "/")) {
                sendError(exchange, 404, "not_found", "No Continuity Works decision-authority route matches this path.");
                return;
            }
            if (!"POST".equals(method)) {
                sendError(exchange, 405, "method_not_allowed", "Decision operation requires POST.");
                return;
            }

            Map<String, Object> body = object(readJson(exchange));
            switch (path.substring(ROUTE_PREFIX.length())) {
                case "/begin" -> begin(exchange, body);
                case "/next" -> next(exchange, body);
                case "/apply" -> apply(exchange, body);
                case "/candidates" -> candidates(exchange, body);
                case "/apply-candidate" -> applyCandidate(exchange, body);
                case "/validate" -> validate(exchange, body);
                case "/finalize" -> finalizeDecision(exchange, body);
                default -> sendError(exchange, 404, "not_found", "Unknown Continuity Works decision-authority operation.");
            }
        } catch (StaleCandidateDictionaryException error) {
            sendError(exchange, 409, "stale_candidate_dictionary", error.getMessage());
        } catch (StaleDecisionException error) {
            sendError(exchange, 409, "stale_decision_state", error.getMessage());
        } catch (IllegalStateException error) {
            sendError(exchange, 409, "decision_state_conflict", error.getMessage());
        } catch (IllegalArgumentException error) {
            sendError(exchange, 400, "invalid_request", error.getMessage());
        } catch (BodyTooLargeException error) {
            sendError(exchange, 413, "request_too_large", error.getMessage());
        } catch (Exception error) {
            sendError(exchange, 500, "decision_authority_error", error.getMessage() == null ? error.getClass().getSimpleName() : error.getMessage());
        } finally {
            exchange.close();
        }
    }

    private void begin(HttpExchange exchange, Map<String, Object> body) throws IOException {
        BlueprintRequest request = decodeRequest(object(required(body, "request")));
        BlueprintDecisionChain.State state = authority.beginDecision(request);
        BlueprintDecisionChain.State existing = sessions.putIfAbsent(state.requestId(), state);
        if (existing != null) {
            throw new IllegalStateException("decision request already exists: " + state.requestId());
        }
        requests.put(state.requestId(), request);
        send(exchange, 200, Map.of("state", stateDocument(state)));
    }

    private void next(HttpExchange exchange, Map<String, Object> body) throws IOException {
        BlueprintDecisionChain.State state = requireCurrentState(decodeState(object(required(body, "state"))));
        send(exchange, 200, stepDocument(authority.nextDecision(state)));
    }

    private void apply(HttpExchange exchange, Map<String, Object> body) throws IOException {
        BlueprintDecisionChain.State supplied = decodeState(object(required(body, "state")));
        BlueprintDecisionChain.State current = requireCurrentState(supplied);
        long expectedRevision = body.containsKey("expected_revision")
            ? longNumber(required(body, "expected_revision"), "expected_revision")
            : supplied.revision();
        String encodedMutations = string(required(body, "encoded_mutations"), "encoded_mutations");
        BlueprintDecisionChain.State revised = authority.applyDecision(current, expectedRevision, encodedMutations);
        replaceCurrentState(current, revised, "refresh before applying inference output");
        send(exchange, 200, Map.of("state", stateDocument(revised)));
    }

    private void candidates(HttpExchange exchange, Map<String, Object> body) throws IOException {
        BlueprintDecisionChain.State supplied = decodeState(object(required(body, "state")));
        BlueprintDecisionChain.State current = requireCurrentState(supplied);
        BlueprintRequest request = requireRequest(current.requestId());
        long expectedRevision = body.containsKey("expected_revision")
            ? longNumber(required(body, "expected_revision"), "expected_revision")
            : supplied.revision();
        String mutatorCode = string(required(body, "mutator_code"), "mutator_code");
        BlueprintDecisionCandidates.Dictionary dictionary = authority.decisionCandidates(
            request, current, expectedRevision, mutatorCode, candidateSource);
        send(exchange, 200, Map.of("dictionary", dictionaryDocument(dictionary)));
    }

    private void applyCandidate(HttpExchange exchange, Map<String, Object> body) throws IOException {
        BlueprintDecisionChain.State supplied = decodeState(object(required(body, "state")));
        BlueprintDecisionChain.State current = requireCurrentState(supplied);
        long expectedRevision = body.containsKey("expected_revision")
            ? longNumber(required(body, "expected_revision"), "expected_revision")
            : supplied.revision();
        BlueprintDecisionCandidates.Dictionary dictionary = decodeDictionary(object(required(body, "dictionary")));
        if (dictionary.revision() != current.revision()) {
            throw new StaleCandidateDictionaryException(
                "candidate dictionary revision " + dictionary.revision()
                    + " does not match authoritative decision revision " + current.revision()
            );
        }
        String localChoiceCode = string(required(body, "local_choice_code"), "local_choice_code");
        BlueprintDecisionChain.State revised = authority.applyCandidateDecision(
            current, expectedRevision, dictionary, localChoiceCode);
        replaceCurrentState(current, revised, "refresh candidate dictionary before applying inference output");
        send(exchange, 200, Map.of("state", stateDocument(revised)));
    }

    private void validate(HttpExchange exchange, Map<String, Object> body) throws IOException {
        BlueprintDecisionChain.State state = requireCurrentState(decodeState(object(required(body, "state"))));
        send(exchange, 200, validationDocument(authority.validateDecision(state)));
    }

    private void finalizeDecision(HttpExchange exchange, Map<String, Object> body) throws IOException {
        BlueprintDecisionChain.State current = requireCurrentState(decodeState(object(required(body, "state"))));
        BlueprintDecisionChain.FinalizedDecision finalized = authority.finalizeDecision(current);
        replaceCurrentState(current, finalized.state(), "refresh before finalization");
        send(exchange, 200, finalizedDocument(finalized));
    }

    private void replaceCurrentState(
        BlueprintDecisionChain.State current,
        BlueprintDecisionChain.State revised,
        String staleMessage
    ) {
        if (!sessions.replace(current.requestId(), current, revised)) {
            throw new StaleDecisionException("decision state changed concurrently; " + staleMessage);
        }
    }

    private BlueprintDecisionChain.State requireCurrentState(BlueprintDecisionChain.State supplied) {
        BlueprintDecisionChain.State current = sessions.get(supplied.requestId());
        if (current == null) {
            throw new StaleDecisionException("unknown decision request: " + supplied.requestId() + "; begin or resume the decision first");
        }
        if (!current.equals(supplied)) {
            throw new StaleDecisionException(
                "stale or modified decision state for " + supplied.requestId()
                    + ": authoritative revision is " + current.revision()
                    + " but supplied revision is " + supplied.revision()
            );
        }
        return current;
    }

    private BlueprintRequest requireRequest(UUID requestId) {
        BlueprintRequest request = requests.get(requestId);
        if (request == null) {
            throw new IllegalStateException(
                "decision request context is unavailable for candidate discovery: " + requestId
                    + "; restore request context with the decision state before requesting dynamic candidates"
            );
        }
        return request;
    }

    private Map<String, Object> profileDocument() {
        BlueprintDecisionChain.Profile profile = authority.decisionProfile();
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("apiVersion", authority.apiVersion().toString());
        out.put("protocolVersion", profile.protocolVersion());
        out.put("referenceInferenceProfile", profile.referenceInferenceProfile());
        out.put("maxOutputTokens", profile.maxOutputTokens());
        out.put("recommendedOutputTokens", profile.recommendedOutputTokens());
        out.put("maxMutationsPerInference", profile.maxMutationsPerInference());
        out.put("stateCarriedAcrossInferences", profile.stateCarriedAcrossInferences());
        out.put("deterministicValidation", profile.deterministicValidation());
        out.put("deterministicFinalization", profile.deterministicFinalization());
        out.put("dynamicCandidateSourceConfigured", dynamicCandidateSourceConfigured());
        out.put("principles", profile.principles());
        List<Object> mutators = new ArrayList<>();
        for (BlueprintDecisionChain.Mutator mutator : profile.mutators()) {
            mutators.add(mutatorDocument(mutator));
        }
        out.put("mutators", mutators);
        return out;
    }

    private static Map<String, Object> mutatorDocument(BlueprintDecisionChain.Mutator mutator) {
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("code", mutator.code());
        out.put("specificationKey", mutator.specificationKey());
        out.put("valueSource", mutator.valueSource().name());
        out.put("fixedValues", mutator.fixedValues());
        out.put("dependsOn", mutator.dependsOn());
        out.put("required", mutator.required());
        out.put("description", mutator.description());
        return out;
    }

    private static Map<String, Object> stateDocument(BlueprintDecisionChain.State state) {
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("requestId", state.requestId().toString());
        out.put("revision", state.revision());
        out.put("selections", state.selections());
        out.put("finalized", state.finalized());
        return out;
    }

    private static Map<String, Object> dictionaryDocument(BlueprintDecisionCandidates.Dictionary dictionary) {
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("protocolVersion", dictionary.protocolVersion());
        out.put("requestId", dictionary.requestId().toString());
        out.put("revision", dictionary.revision());
        out.put("mutatorCode", dictionary.mutatorCode());
        out.put("sourceVersion", dictionary.sourceVersion());
        out.put("dictionaryId", dictionary.dictionaryId());
        List<Object> choices = new ArrayList<>();
        for (BlueprintDecisionCandidates.Choice choice : dictionary.choices()) {
            choices.add(Map.of(
                "localCode", choice.localCode(),
                "semanticValue", choice.semanticValue()
            ));
        }
        out.put("choices", choices);
        return out;
    }

    private static Map<String, Object> validationDocument(BlueprintDecisionChain.Validation validation) {
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("valid", validation.valid());
        out.put("readyToFinalize", validation.readyToFinalize());
        out.put("missingRequired", validation.missingRequired());
        out.put("findings", validation.findings());
        return out;
    }

    private static Map<String, Object> stepDocument(BlueprintDecisionChain.Step step) {
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("state", stateDocument(step.state()));
        List<Object> next = new ArrayList<>();
        for (BlueprintDecisionChain.Mutator mutator : step.nextMutators()) next.add(mutatorDocument(mutator));
        out.put("nextMutators", next);
        out.put("validation", validationDocument(step.validation()));
        out.put("compactPrompt", step.compactPrompt());
        return out;
    }

    private static Map<String, Object> finalizedDocument(BlueprintDecisionChain.FinalizedDecision finalized) {
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        out.put("state", stateDocument(finalized.state()));
        List<Object> specs = new ArrayList<>();
        for (BlueprintSpecification specification : finalized.specifications()) {
            specs.add(Map.of(
                "key", specification.key(),
                "value", specification.value(),
                "requirement", specification.requirement().name()
            ));
        }
        out.put("specifications", specs);
        return out;
    }

    private BlueprintRequest decodeRequest(Map<String, Object> value) {
        UUID requestId = uuid(required(value, "requestId"), "requestId");
        UUID companionUuid = uuid(required(value, "companionUuid"), "companionUuid");
        UUID ownerUuid = uuid(required(value, "ownerUuid"), "ownerUuid");
        String dimensionId = string(required(value, "dimensionId"), "dimensionId");
        String buildPurpose = string(required(value, "buildPurpose"), "buildPurpose");
        ConstructionVolume volume = decodeVolume(object(required(value, "constructionVolume")));
        BlockPosition preferredOrigin = decodePosition(object(required(value, "preferredOrigin")));
        Facing preferredFacing = enumValue(Facing.class, required(value, "preferredFacing"), "preferredFacing");

        List<BlueprintSpecification> specifications = new ArrayList<>();
        for (Object entry : list(value.get("specifications"), "specifications")) {
            Map<String, Object> spec = object(entry);
            specifications.add(new BlueprintSpecification(
                string(required(spec, "key"), "specifications.key"),
                string(required(spec, "value"), "specifications.value"),
                enumValue(BlueprintSpecification.Requirement.class, spec.getOrDefault("requirement", "PREFERRED"), "specifications.requirement")
            ));
        }

        List<MaterialAvailability> materials = new ArrayList<>();
        for (Object entry : list(value.get("availableMaterials"), "availableMaterials")) {
            Map<String, Object> material = object(entry);
            materials.add(new MaterialAvailability(
                string(required(material, "materialId"), "availableMaterials.materialId"),
                longNumber(required(material, "availableCount"), "availableMaterials.availableCount"),
                stringSet(material.get("tags"), "availableMaterials.tags")
            ));
        }

        List<SiteCandidate> sites = new ArrayList<>();
        for (Object entry : list(value.get("candidateSites"), "candidateSites")) {
            Map<String, Object> site = object(entry);
            sites.add(new SiteCandidate(
                string(required(site, "siteId"), "candidateSites.siteId"),
                decodePosition(object(required(site, "origin"))),
                enumValue(Facing.class, required(site, "facing"), "candidateSites.facing"),
                decodeBounds(object(required(site, "usableBounds"))),
                doubleNumber(required(site, "suitability"), "candidateSites.suitability"),
                stringMap(site.get("attributes"), "candidateSites.attributes")
            ));
        }

        return new BlueprintRequest(
            requestId,
            companionUuid,
            ownerUuid,
            dimensionId,
            buildPurpose,
            volume,
            preferredOrigin,
            preferredFacing,
            specifications,
            materials,
            sites,
            stringSet(value.get("permittedStyles"), "permittedStyles")
        );
    }

    private static ConstructionVolume decodeVolume(Map<String, Object> value) {
        return new ConstructionVolume(
            uuid(required(value, "volumeId"), "constructionVolume.volumeId"),
            decodeBounds(object(required(value, "bounds"))),
            longNumber(required(value, "snapshotEpoch"), "constructionVolume.snapshotEpoch"),
            stringMap(value.get("attributes"), "constructionVolume.attributes")
        );
    }

    private static Bounds decodeBounds(Map<String, Object> value) {
        return new Bounds(
            decodePosition(object(required(value, "min"))),
            decodePosition(object(required(value, "max")))
        );
    }

    private static BlockPosition decodePosition(Map<String, Object> value) {
        return new BlockPosition(
            integer(required(value, "x"), "position.x"),
            integer(required(value, "y"), "position.y"),
            integer(required(value, "z"), "position.z")
        );
    }

    private static BlueprintDecisionChain.State decodeState(Map<String, Object> value) {
        UUID requestId = uuid(required(value, "requestId"), "state.requestId");
        long revision = longNumber(required(value, "revision"), "state.revision");
        boolean finalized = bool(required(value, "finalized"), "state.finalized");
        Map<String, String> selections = stringMap(value.get("selections"), "state.selections");
        return new BlueprintDecisionChain.State(requestId, revision, selections, finalized);
    }

    private static BlueprintDecisionCandidates.Dictionary decodeDictionary(Map<String, Object> value) {
        List<BlueprintDecisionCandidates.Choice> choices = new ArrayList<>();
        for (Object entry : list(required(value, "choices"), "dictionary.choices")) {
            Map<String, Object> choice = object(entry);
            choices.add(new BlueprintDecisionCandidates.Choice(
                string(required(choice, "localCode"), "dictionary.choices.localCode"),
                string(required(choice, "semanticValue"), "dictionary.choices.semanticValue")
            ));
        }
        return new BlueprintDecisionCandidates.Dictionary(
            string(required(value, "protocolVersion"), "dictionary.protocolVersion"),
            uuid(required(value, "requestId"), "dictionary.requestId"),
            longNumber(required(value, "revision"), "dictionary.revision"),
            string(required(value, "mutatorCode"), "dictionary.mutatorCode"),
            string(required(value, "sourceVersion"), "dictionary.sourceVersion"),
            string(required(value, "dictionaryId"), "dictionary.dictionaryId"),
            choices
        );
    }

    private Object readJson(HttpExchange exchange) throws IOException {
        String contentType = exchange.getRequestHeaders().getFirst("Content-Type");
        if (contentType != null && !contentType.toLowerCase().startsWith("application/json")) {
            throw new IllegalArgumentException("Content-Type must be application/json");
        }
        byte[] body = readBounded(exchange.getRequestBody(), maxBodyBytes);
        if (body.length == 0) return Map.of();
        return Json.parse(new String(body, StandardCharsets.UTF_8));
    }

    private static byte[] readBounded(InputStream input, int limit) throws IOException {
        byte[] buffer = new byte[Math.min(8192, limit + 1)];
        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream(Math.min(limit, 8192));
        int total = 0;
        for (int read; (read = input.read(buffer)) != -1;) {
            total += read;
            if (total > limit) throw new BodyTooLargeException("JSON request exceeds " + limit + " bytes");
            out.write(buffer, 0, read);
        }
        return out.toByteArray();
    }

    private static void send(HttpExchange exchange, int status, Object payload) throws IOException {
        byte[] body = Json.stringify(payload).getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.getResponseHeaders().set("Cache-Control", "no-store");
        exchange.sendResponseHeaders(status, body.length);
        exchange.getResponseBody().write(body);
    }

    private static void sendError(HttpExchange exchange, int status, String code, String message) throws IOException {
        send(exchange, status, Map.of("error", code, "message", message == null ? "" : message));
    }

    private static Object required(Map<String, Object> value, String key) {
        if (!value.containsKey(key) || value.get(key) == null) throw new IllegalArgumentException("missing required field: " + key);
        return value.get(key);
    }

    private static Map<String, Object> object(Object value) {
        if (!(value instanceof Map<?, ?> map)) throw new IllegalArgumentException("expected JSON object");
        LinkedHashMap<String, Object> out = new LinkedHashMap<>();
        for (Map.Entry<?, ?> entry : map.entrySet()) {
            if (!(entry.getKey() instanceof String key)) throw new IllegalArgumentException("JSON object key must be a string");
            out.put(key, entry.getValue());
        }
        return out;
    }

    private static List<Object> list(Object value, String field) {
        if (value == null) return List.of();
        if (!(value instanceof List<?> list)) throw new IllegalArgumentException(field + " must be an array");
        return List.copyOf(list);
    }

    private static String string(Object value, String field) {
        if (!(value instanceof String text)) throw new IllegalArgumentException(field + " must be a string");
        return text;
    }

    private static UUID uuid(Object value, String field) {
        try {
            return UUID.fromString(string(value, field));
        } catch (IllegalArgumentException error) {
            throw new IllegalArgumentException(field + " must be a UUID", error);
        }
    }

    private static long longNumber(Object value, String field) {
        if (!(value instanceof Number number)) throw new IllegalArgumentException(field + " must be a number");
        if (value instanceof Double || value instanceof Float) {
            double d = number.doubleValue();
            if (!Double.isFinite(d) || d != Math.rint(d)) throw new IllegalArgumentException(field + " must be an integer");
        }
        return number.longValue();
    }

    private static int integer(Object value, String field) {
        long number = longNumber(value, field);
        if (number < Integer.MIN_VALUE || number > Integer.MAX_VALUE) throw new IllegalArgumentException(field + " is outside integer range");
        return (int) number;
    }

    private static double doubleNumber(Object value, String field) {
        if (!(value instanceof Number number)) throw new IllegalArgumentException(field + " must be a number");
        double d = number.doubleValue();
        if (!Double.isFinite(d)) throw new IllegalArgumentException(field + " must be finite");
        return d;
    }

    private static boolean bool(Object value, String field) {
        if (!(value instanceof Boolean flag)) throw new IllegalArgumentException(field + " must be a boolean");
        return flag;
    }

    private static Map<String, String> stringMap(Object value, String field) {
        if (value == null) return Map.of();
        Map<String, Object> raw = object(value);
        LinkedHashMap<String, String> out = new LinkedHashMap<>();
        for (Map.Entry<String, Object> entry : raw.entrySet()) {
            out.put(entry.getKey(), string(entry.getValue(), field + "." + entry.getKey()));
        }
        return out;
    }

    private static Set<String> stringSet(Object value, String field) {
        if (value == null) return Set.of();
        List<Object> raw = list(value, field);
        LinkedHashSet<String> out = new LinkedHashSet<>();
        for (Object entry : raw) out.add(string(entry, field));
        return out;
    }

    private static <E extends Enum<E>> E enumValue(Class<E> type, Object value, String field) {
        String text = string(value, field).trim().toUpperCase();
        try {
            return Enum.valueOf(type, text);
        } catch (IllegalArgumentException error) {
            throw new IllegalArgumentException(field + " has unsupported value: " + text, error);
        }
    }

    private static final class StaleCandidateDictionaryException extends RuntimeException {
        private static final long serialVersionUID = 1L;
        StaleCandidateDictionaryException(String message) { super(message); }
    }

    private static final class StaleDecisionException extends RuntimeException {
        private static final long serialVersionUID = 1L;
        StaleDecisionException(String message) { super(message); }
    }

    private static final class BodyTooLargeException extends RuntimeException {
        private static final long serialVersionUID = 1L;
        BodyTooLargeException(String message) { super(message); }
    }

    /** Small strict JSON codec kept inside the transport so no model/runtime dependency is added. */
    static final class Json {
        private final String text;
        private int index;

        private Json(String text) {
            this.text = Objects.requireNonNull(text, "text");
        }

        static Object parse(String text) {
            Json parser = new Json(text);
            Object value = parser.readValue();
            parser.skipWhitespace();
            if (parser.index != parser.text.length()) throw parser.error("unexpected trailing JSON content");
            return value;
        }

        static String stringify(Object value) {
            StringBuilder out = new StringBuilder();
            writeValue(out, value);
            return out.toString();
        }

        private Object readValue() {
            skipWhitespace();
            if (index >= text.length()) throw error("unexpected end of JSON");
            return switch (text.charAt(index)) {
                case '{' -> readObject();
                case '[' -> readArray();
                case '"' -> readString();
                case 't' -> readLiteral("true", Boolean.TRUE);
                case 'f' -> readLiteral("false", Boolean.FALSE);
                case 'n' -> readLiteral("null", null);
                default -> readNumber();
            };
        }

        private Map<String, Object> readObject() {
            expect('{');
            LinkedHashMap<String, Object> out = new LinkedHashMap<>();
            skipWhitespace();
            if (take('}')) return out;
            while (true) {
                skipWhitespace();
                if (index >= text.length() || text.charAt(index) != '"') throw error("JSON object key must be a string");
                String key = readString();
                if (out.containsKey(key)) throw error("duplicate JSON object key: " + key);
                skipWhitespace();
                expect(':');
                out.put(key, readValue());
                skipWhitespace();
                if (take('}')) return out;
                expect(',');
            }
        }

        private List<Object> readArray() {
            expect('[');
            ArrayList<Object> out = new ArrayList<>();
            skipWhitespace();
            if (take(']')) return out;
            while (true) {
                out.add(readValue());
                skipWhitespace();
                if (take(']')) return out;
                expect(',');
            }
        }

        private String readString() {
            expect('"');
            StringBuilder out = new StringBuilder();
            while (index < text.length()) {
                char c = text.charAt(index++);
                if (c == '"') return out.toString();
                if (c == '\\') {
                    if (index >= text.length()) throw error("unterminated JSON escape");
                    char escaped = text.charAt(index++);
                    switch (escaped) {
                        case '"', '\\', '/' -> out.append(escaped);
                        case 'b' -> out.append('\b');
                        case 'f' -> out.append('\f');
                        case 'n' -> out.append('\n');
                        case 'r' -> out.append('\r');
                        case 't' -> out.append('\t');
                        case 'u' -> out.append(readUnicodeEscape());
                        default -> throw error("unsupported JSON escape: \\" + escaped);
                    }
                } else {
                    if (c < 0x20) throw error("unescaped JSON control character");
                    out.append(c);
                }
            }
            throw error("unterminated JSON string");
        }

        private char readUnicodeEscape() {
            if (index + 4 > text.length()) throw error("short unicode escape");
            int value = 0;
            for (int i = 0; i < 4; i++) {
                int digit = Character.digit(text.charAt(index++), 16);
                if (digit < 0) throw error("invalid unicode escape");
                value = (value << 4) | digit;
            }
            return (char) value;
        }

        private Object readNumber() {
            int start = index;
            if (take('-')) { }
            if (index >= text.length()) throw error("invalid JSON number");
            if (take('0')) {
                if (index < text.length() && Character.isDigit(text.charAt(index))) throw error("leading zero in JSON number");
            } else {
                if (!Character.isDigit(text.charAt(index))) throw error("invalid JSON value");
                while (index < text.length() && Character.isDigit(text.charAt(index))) index++;
            }
            boolean decimal = false;
            if (take('.')) {
                decimal = true;
                if (index >= text.length() || !Character.isDigit(text.charAt(index))) throw error("invalid JSON fraction");
                while (index < text.length() && Character.isDigit(text.charAt(index))) index++;
            }
            if (index < text.length() && (text.charAt(index) == 'e' || text.charAt(index) == 'E')) {
                decimal = true;
                index++;
                if (index < text.length() && (text.charAt(index) == '+' || text.charAt(index) == '-')) index++;
                if (index >= text.length() || !Character.isDigit(text.charAt(index))) throw error("invalid JSON exponent");
                while (index < text.length() && Character.isDigit(text.charAt(index))) index++;
            }
            String raw = text.substring(start, index);
            try {
                return decimal ? Double.parseDouble(raw) : Long.parseLong(raw);
            } catch (NumberFormatException error) {
                throw error("invalid JSON number");
            }
        }

        private Object readLiteral(String literal, Object value) {
            if (!text.regionMatches(index, literal, 0, literal.length())) throw error("invalid JSON literal");
            index += literal.length();
            return value;
        }

        private void skipWhitespace() {
            while (index < text.length()) {
                char c = text.charAt(index);
                if (c == ' ' || c == '\n' || c == '\r' || c == '\t') index++;
                else break;
            }
        }

        private void expect(char expected) {
            skipWhitespace();
            if (index >= text.length() || text.charAt(index) != expected) throw error("expected '" + expected + "'");
            index++;
        }

        private boolean take(char expected) {
            if (index < text.length() && text.charAt(index) == expected) {
                index++;
                return true;
            }
            return false;
        }

        private IllegalArgumentException error(String message) {
            return new IllegalArgumentException(message + " at JSON offset " + index);
        }

        private static void writeValue(StringBuilder out, Object value) {
            if (value == null) {
                out.append("null");
            } else if (value instanceof String text) {
                writeString(out, text);
            } else if (value instanceof Number || value instanceof Boolean) {
                out.append(value);
            } else if (value instanceof Enum<?> enumeration) {
                writeString(out, enumeration.name());
            } else if (value instanceof Map<?, ?> map) {
                out.append('{');
                boolean first = true;
                for (Map.Entry<?, ?> entry : map.entrySet()) {
                    if (!(entry.getKey() instanceof String key)) throw new IllegalArgumentException("JSON object key must be a string");
                    if (!first) out.append(',');
                    first = false;
                    writeString(out, key);
                    out.append(':');
                    writeValue(out, entry.getValue());
                }
                out.append('}');
            } else if (value instanceof Iterable<?> values) {
                out.append('[');
                boolean first = true;
                for (Object entry : values) {
                    if (!first) out.append(',');
                    first = false;
                    writeValue(out, entry);
                }
                out.append(']');
            } else {
                writeString(out, value.toString());
            }
        }

        private static void writeString(StringBuilder out, String value) {
            out.append('"');
            for (int i = 0; i < value.length(); i++) {
                char c = value.charAt(i);
                switch (c) {
                    case '"' -> out.append("\\\"");
                    case '\\' -> out.append("\\\\");
                    case '\b' -> out.append("\\b");
                    case '\f' -> out.append("\\f");
                    case '\n' -> out.append("\\n");
                    case '\r' -> out.append("\\r");
                    case '\t' -> out.append("\\t");
                    default -> {
                        if (c < 0x20) out.append(String.format("\\u%04x", (int) c));
                        else out.append(c);
                    }
                }
            }
            out.append('"');
        }
    }
}
