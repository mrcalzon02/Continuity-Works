package io.continuityworks.blueprint.runtime;

import com.google.gson.*;
import io.continuityworks.api.blueprint.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

final class FacilityCorpusPlanner {
    static final int MAX_CANDIDATES = 8;
    static final int MAX_OPERATIONS = 131_072;
    private static final String ROOT = "continuityworks/facility_library/";
    private volatile Index index;

    Optional<BlueprintProposal> plan(BlueprintRequest request) {
        Map<String, BlueprintSpecification> specs = first(request.specifications());
        boolean explicit = specs.containsKey("REFERENCE") || specs.containsKey("ARCHETYPE") || specs.containsKey("CATEGORY");
        boolean geometryOverride = specs.containsKey("STYLE") || specs.containsKey("ROOF")
            || specs.containsKey("FLOORS") || specs.containsKey("ENTRANCE");
        if (!explicit && (geometryOverride || !request.permittedStyles().isEmpty())) return Optional.empty();

        List<Scored> ranked = rank(request, specs);
        if (ranked.isEmpty()) return requiredSelector(specs)
            ? fail("No required Continuity Works corpus selector matched a bundled reference.")
            : Optional.empty();

        Candidate best = null;
        int opened = 0;
        for (Scored scored : ranked) {
            if (opened++ >= MAX_CANDIDATES) break;
            Candidate candidate = load(scored, request, specs);
            if (candidate == null) continue;
            if (best == null || candidate.score() > best.score()) best = candidate;
        }
        if (best == null) return requiredSelector(specs)
            ? fail("No required Continuity Works corpus reference fits the selected construction volume.")
            : Optional.empty();
        return Optional.of(compile(best, request, specs));
    }

    private static <T> Optional<T> fail(String message) {
        throw new IllegalArgumentException(message);
    }

    private Candidate load(Scored scored, BlueprintRequest request, Map<String, BlueprintSpecification> specs) {
        JsonObject ref = json(scored.entry().path());
        String refId = text(ref, "reference_id");
        String archetype = text(ref, "archetype_id");
        if (specs.containsKey("REFERENCE") && !idMatches(specs.get("REFERENCE").value(), refId)) return null;
        if (specs.containsKey("ARCHETYPE") && !idMatches(specs.get("ARCHETYPE").value(), archetype)) return null;

        JsonArray size = ref.getAsJsonArray("size");
        int sw = size.get(0).getAsInt(), sh = size.get(1).getAsInt(), sd = size.get(2).getAsInt();
        Dims dims = rotateDims(sw, sh, sd, request.preferredFacing());
        Bounds volume = request.constructionVolume().bounds();
        if (dims.w() > volume.width() || dims.h() > volume.height() || dims.d() > volume.depth()) return null;

        int score = scored.score();
        BlueprintSpecification requestedSize = specs.get("SIZE");
        String sizeClass = sizeClass(dims, volume);
        if (requestedSize != null) score += norm(requestedSize.value()).equals(sizeClass) ? 80 : -20;
        return new Candidate(scored.entry(), ref, refId, archetype, text(ref, "corporate_language_id"), dims, sizeClass, score);
    }

    private BlueprintProposal compile(Candidate c, BlueprintRequest request, Map<String, BlueprintSpecification> specs) {
        Index idx = index();
        Entry corporate = idx.byId().get(c.corporateId());
        if (corporate == null) throw new IllegalStateException("Missing corporate palette " + c.corporateId());
        JsonObject paletteJson = json(corporate.path()).getAsJsonObject("palette");
        Map<String, String> roles = new HashMap<>();
        for (Map.Entry<String, JsonElement> e : paletteJson.entrySet()) roles.put(e.getKey(), e.getValue().getAsString());

        int sw = c.ref().getAsJsonArray("size").get(0).getAsInt();
        int sd = c.ref().getAsJsonArray("size").get(2).getAsInt();
        TreeMap<P, String> blocks = new TreeMap<>();
        for (JsonElement element : c.ref().getAsJsonArray("blueprint")) {
            JsonObject p = element.getAsJsonObject();
            String op = text(p, "op");
            String block = p.has("block") ? p.get("block").getAsString() : roles.get(text(p, "role"));
            if (block == null || !block.startsWith("minecraft:")) throw new IllegalStateException("Invalid corpus block " + block);
            switch (op) {
                case "block" -> put(blocks, rotate(v3(p.getAsJsonArray("pos")), sw, sd, request.preferredFacing()), block, c.dims());
                case "fill_box" -> box(blocks, p, block, false, sw, sd, request.preferredFacing(), c.dims());
                case "hollow_box" -> box(blocks, p, block, true, sw, sd, request.preferredFacing(), c.dims());
                case "line" -> line(blocks, p, block, sw, sd, request.preferredFacing(), c.dims());
                case "cylinder" -> cylinder(blocks, p, block, sw, sd, request.preferredFacing(), c.dims());
                default -> throw new IllegalStateException("Unsupported corpus primitive " + op);
            }
        }

        SortedSet<String> materials = new TreeSet<>(blocks.values());
        List<PaletteEntry> palette = new ArrayList<>();
        Map<String, String> key = new HashMap<>();
        int pi = 0;
        for (String block : materials) {
            String k = "p" + pi++;
            key.put(block, k);
            palette.add(new PaletteEntry(k, block, block, Map.of("source", "facility_corpus")));
        }

        List<PlacementOperation> ops = new ArrayList<>(blocks.size());
        int seq = 0;
        for (Map.Entry<P, String> e : blocks.entrySet()) {
            P p = e.getKey();
            ops.add(new PlacementOperation(seq++, PlacementOperation.Kind.PLACE,
                new BlockPosition(p.x(), p.y(), p.z()), key.get(e.getValue())));
        }

        BlockPosition anchor = anchor(request.preferredOrigin(), request.constructionVolume().bounds(), c.dims());
        String version = "facility-corpus/" + idx.version() + "/v" + c.ref().get("version").getAsInt();
        String hash = sha256(canonical(c, request, anchor, palette, ops));
        UUID id = UUID.nameUUIDFromBytes((version + ":" + hash).getBytes(StandardCharsets.UTF_8));
        MaterialManifest manifest = manifest(id, palette, ops, request.availableMaterials());
        List<MaterialIssue> issues = issues(manifest);
        List<SpecificationResolution> ledger = ledger(c, request, specs);
        List<BlueprintWarning> warnings = warnings(ledger, specs);
        if (!issues.isEmpty()) warnings.add(new BlueprintWarning("MATERIALS_INCOMPLETE",
            BlueprintWarning.Severity.WARNING, "Current material snapshot cannot satisfy the full proposal."));

        Bounds local = new Bounds(new BlockPosition(0, 0, 0), new BlockPosition(c.dims().w()-1, c.dims().h()-1, c.dims().d()-1));
        Map<String, String> meta = Map.of(
            "reference", c.refId(), "archetype", c.archetype(),
            "category", c.entry().category(), "corporate_language", c.corporateId(),
            "size_class", c.sizeClass(), "planner", "lazy_facility_corpus"
        );
        double confidence = warnings.stream().anyMatch(w -> w.severity() == BlueprintWarning.Severity.ERROR) ? 0.45 : 0.98;
        BlueprintProposal proposal = new BlueprintProposal(id, version, "SHA-256", hash, request.dimensionId(),
            request.constructionVolume(), local, anchor, request.preferredFacing(), ledger, palette, manifest, ops,
            List.of(), issues, new WorkloadEstimate(ops.size(), 0, 0, ops.size()),
            new PreviewMetadata(request.buildPurpose(),
                c.ref().has("description") ? c.ref().get("description").getAsString() : c.refId(),
                c.entry().category(), meta),
            confidence, warnings);
        if (!proposal.allOperationsInsideConstructionVolume()) throw new IllegalStateException("Corpus proposal escaped construction volume");
        return proposal;
    }

    private List<Scored> rank(BlueprintRequest request, Map<String, BlueprintSpecification> specs) {
        List<Scored> out = new ArrayList<>();
        Set<String> purpose = tokens(request.buildPurpose());
        for (Entry e : index().references()) {
            int score = "baseline".equalsIgnoreCase(e.status()) ? 5 : 0;
            BlueprintSpecification ref = specs.get("REFERENCE");
            BlueprintSpecification cat = specs.get("CATEGORY");
            BlueprintSpecification arch = specs.get("ARCHETYPE");
            if (ref != null) {
                if (!idMatches(ref.value(), e.id())) continue;
                score += 10_000;
            }
            if (cat != null) {
                if (!clean(cat.value()).equals(clean(e.category()))) continue;
                score += 1_000;
            }
            String hay = clean(e.id() + " " + e.category() + " " + e.path());
            if (arch != null) {
                String a = clean(slug(arch.value()));
                if (!hay.contains(a)) continue;
                score += 800;
            }
            for (String token : purpose) if (token.length() > 2 && hay.contains(token)) score += 20;
            if (ref == null && cat == null && arch == null && score < 30) continue;
            out.add(new Scored(e, score));
        }
        out.sort(Comparator.comparingInt(Scored::score).reversed().thenComparing(s -> s.entry().id()));
        return out;
    }

    private Index index() {
        Index current = index;
        if (current != null) return current;
        synchronized (this) {
            if (index != null) return index;
            JsonObject manifest = json("manifest.json");
            List<Entry> refs = new ArrayList<>();
            Map<String, Entry> byId = new HashMap<>();
            for (JsonElement element : manifest.getAsJsonArray("entries")) {
                JsonObject o = element.getAsJsonObject();
                Entry e = new Entry(text(o,"id"), text(o,"kind"), text(o,"category"), text(o,"path"),
                    o.has("status") ? o.get("status").getAsString() : "");
                byId.put(e.id(), e);
                if ("facility_reference".equals(e.kind())) refs.add(e);
            }
            refs.sort(Comparator.comparing(Entry::id));
            return index = new Index(manifest.get("library_version").getAsString(), List.copyOf(refs), Map.copyOf(byId));
        }
    }

    private static JsonObject json(String path) {
        try (InputStream in = FacilityCorpusPlanner.class.getClassLoader().getResourceAsStream(ROOT + path)) {
            if (in == null) throw new IllegalStateException("Missing bundled corpus resource " + ROOT + path);
            return JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
        } catch (IOException e) {
            throw new IllegalStateException("Failed reading corpus resource " + path, e);
        }
    }

    private static void box(Map<P,String> blocks, JsonObject o, String block, boolean hollow,
                            int sw, int sd, Facing facing, Dims dims) {
        int[] a=v3(o.getAsJsonArray("min")), b=v3(o.getAsJsonArray("max"));
        for(int x=a[0];x<=b[0];x++) for(int y=a[1];y<=b[1];y++) for(int z=a[2];z<=b[2];z++)
            if(!hollow||x==a[0]||x==b[0]||y==a[1]||y==b[1]||z==a[2]||z==b[2])
                put(blocks,rotate(new int[]{x,y,z},sw,sd,facing),block,dims);
    }

    private static void line(Map<P,String> blocks, JsonObject o, String block,
                             int sw, int sd, Facing facing, Dims dims) {
        int[] a=v3(o.getAsJsonArray("start")), b=v3(o.getAsJsonArray("end"));
        int dx=b[0]-a[0],dy=b[1]-a[1],dz=b[2]-a[2],n=Math.max(Math.abs(dx),Math.max(Math.abs(dy),Math.abs(dz)));
        if(n==0){put(blocks,rotate(a,sw,sd,facing),block,dims);return;}
        for(int i=0;i<=n;i++){double t=(double)i/n;put(blocks,rotate(new int[]{
            (int)Math.round(a[0]+dx*t),(int)Math.round(a[1]+dy*t),(int)Math.round(a[2]+dz*t)},sw,sd,facing),block,dims);}
    }

    private static void cylinder(Map<P,String> blocks, JsonObject o, String block,
                                 int sw, int sd, Facing facing, Dims dims) {
        JsonArray c=o.getAsJsonArray("center"); int cx=c.get(0).getAsInt(),cz=c.get(1).getAsInt();
        int r=o.get("radius").getAsInt(),y0=o.get("y_min").getAsInt(),y1=o.get("y_max").getAsInt();
        boolean solid=o.has("mode")&&"solid".equals(o.get("mode").getAsString()),caps=o.has("caps")&&o.get("caps").getAsBoolean();
        for(int x=cx-r;x<=cx+r;x++) for(int z=cz-r;z<=cz+r;z++){
            if((x-cx)*(x-cx)+(z-cz)*(z-cz)>r*r)continue;
            boolean edge=(x+1-cx)*(x+1-cx)+(z-cz)*(z-cz)>r*r||(x-1-cx)*(x-1-cx)+(z-cz)*(z-cz)>r*r
                ||(x-cx)*(x-cx)+(z+1-cz)*(z+1-cz)>r*r||(x-cx)*(x-cx)+(z-1-cz)*(z-1-cz)>r*r;
            for(int y=y0;y<=y1;y++)if(solid||edge||(caps&&(y==y0||y==y1)))put(blocks,rotate(new int[]{x,y,z},sw,sd,facing),block,dims);
        }
    }

    private static void put(Map<P,String> blocks,int[] p,String block,Dims d){
        if(p[0]<0||p[0]>=d.w()||p[1]<0||p[1]>=d.h()||p[2]<0||p[2]>=d.d())throw new IllegalStateException("Corpus primitive out of bounds");
        blocks.put(new P(p[0],p[1],p[2]),block);
        if(blocks.size()>MAX_OPERATIONS)throw new IllegalArgumentException("Corpus blueprint exceeds "+MAX_OPERATIONS+" operations");
    }

    private static int[] rotate(int[] p,int w,int d,Facing f){return switch(f){
        case SOUTH->new int[]{w-1-p[0],p[1],d-1-p[2]};
        case EAST->new int[]{d-1-p[2],p[1],p[0]};
        case WEST->new int[]{p[2],p[1],w-1-p[0]};
        default->new int[]{p[0],p[1],p[2]};};}

    private static Dims rotateDims(int w,int h,int d,Facing f){return switch(f){case EAST,WEST->new Dims(d,h,w);default->new Dims(w,h,d);};}
    private static BlockPosition anchor(BlockPosition p,Bounds b,Dims d){return new BlockPosition(
        clamp(p.x()-d.w()/2,b.min().x(),b.max().x()-d.w()+1),clamp(p.y(),b.min().y(),b.max().y()-d.h()+1),
        clamp(p.z()-d.d()/2,b.min().z(),b.max().z()-d.d()+1));}
    private static int clamp(int v,int a,int b){return b<a?a:Math.max(a,Math.min(b,v));}

    private static String sizeClass(Dims d,Bounds b){double r=Math.max((double)d.w()/b.width(),Math.max((double)d.h()/b.height(),(double)d.d()/b.depth()));
        return r<=.30?"TINY":r<=.50?"COMPACT":r<=.70?"STANDARD":r<=.90?"LARGE":"FILL";}

    private static MaterialManifest manifest(UUID id,List<PaletteEntry> palette,List<PlacementOperation> ops,List<MaterialAvailability> have){
        Map<String,String> byKey=new HashMap<>();for(PaletteEntry p:palette)byKey.put(p.key(),p.materialId());
        Map<String,Long> req=new TreeMap<>(),av=new TreeMap<>(),missing=new TreeMap<>();
        for(PlacementOperation o:ops){String m=byKey.get(o.paletteKey());if(m!=null)req.merge(m,1L,Long::sum);}
        for(MaterialAvailability a:have)av.merge(a.materialId(),a.availableCount(),Long::sum);
        for(Map.Entry<String,Long> e:req.entrySet()){long n=av.getOrDefault(e.getKey(),0L);if(n<e.getValue())missing.put(e.getKey(),e.getValue()-n);}
        return new MaterialManifest(id,req,av,missing);}

    private static List<MaterialIssue> issues(MaterialManifest m){List<MaterialIssue> out=new ArrayList<>();
        for(Map.Entry<String,Long> e:m.missing().entrySet())out.add(new MaterialIssue(e.getKey(),MaterialIssue.Kind.MISSING,m.required().get(e.getKey()),m.available().getOrDefault(e.getKey(),0L),"Insufficient material."));
        return List.copyOf(out);}

    private static List<SpecificationResolution> ledger(Candidate c,BlueprintRequest r,Map<String,BlueprintSpecification>s){
        List<SpecificationResolution> out=new ArrayList<>();
        sel(out,s.get("REFERENCE"),"REFERENCE",c.refId());sel(out,s.get("ARCHETYPE"),"ARCHETYPE",c.archetype());sel(out,s.get("CATEGORY"),"CATEGORY",c.entry().category());
        BlueprintSpecification size=s.get("SIZE");
        out.add(size==null?new SpecificationResolution("SIZE","",c.sizeClass(),SpecificationResolution.Status.DEFAULTED,"Derived from fixed reference footprint.")
            :new SpecificationResolution("SIZE",size.value(),c.sizeClass(),norm(size.value()).equals(c.sizeClass())?SpecificationResolution.Status.APPLIED:SpecificationResolution.Status.CONFLICT,"Fixed corpus reference is not rescaled."));
        Set<String> handled=Set.of("REFERENCE","ARCHETYPE","CATEGORY","SIZE","PURPOSE_DETAIL");
        for(BlueprintSpecification spec:r.specifications())if(!handled.contains(spec.key()))out.add(new SpecificationResolution(spec.key(),spec.value(),"",SpecificationResolution.Status.UNSUPPORTED,"Fixed corpus reference does not mutate this geometry field."));
        BlueprintSpecification detail=s.get("PURPOSE_DETAIL");if(detail!=null)out.add(new SpecificationResolution("PURPOSE_DETAIL",detail.value(),detail.value(),SpecificationResolution.Status.APPLIED,"Semantic metadata preserved."));
        return List.copyOf(out);}

    private static void sel(List<SpecificationResolution>out,BlueprintSpecification s,String key,String value){
        out.add(s==null?new SpecificationResolution(key,"",value,SpecificationResolution.Status.DEFAULTED,"Deterministically selected from bundled corpus.")
            :new SpecificationResolution(key,s.value(),value,idMatches(s.value(),value)?SpecificationResolution.Status.APPLIED:SpecificationResolution.Status.CONFLICT,""));}

    private static List<BlueprintWarning> warnings(List<SpecificationResolution> ledger,Map<String,BlueprintSpecification> specs){
        List<BlueprintWarning> out=new ArrayList<>();
        for(SpecificationResolution r:ledger)if(r.status()==SpecificationResolution.Status.CONFLICT||r.status()==SpecificationResolution.Status.UNSUPPORTED){
            BlueprintSpecification s=specs.get(r.key());BlueprintWarning.Severity sev=s!=null&&s.requirement()==BlueprintSpecification.Requirement.REQUIRED?BlueprintWarning.Severity.ERROR:BlueprintWarning.Severity.WARNING;
            out.add(new BlueprintWarning("CORPUS_"+r.status(),sev,r.key()+"="+r.requestedValue()+" -> "+r.resolvedValue()));}
        return out;}

    private static String canonical(Candidate c,BlueprintRequest r,BlockPosition a,List<PaletteEntry> p,List<PlacementOperation>o){
        StringBuilder s=new StringBuilder("corpus|").append(c.refId()).append('|').append(r.dimensionId()).append('|').append(r.constructionVolume().volumeId()).append('|').append(r.constructionVolume().snapshotEpoch()).append('|').append(a).append('|').append(r.preferredFacing());
        for(PaletteEntry e:p)s.append('|').append(e.key()).append('=').append(e.blockState());for(PlacementOperation e:o)s.append('|').append(e.sequence()).append(':').append(e.relativePosition()).append(':').append(e.paletteKey());return s.toString();}

    private static String sha256(String v){try{byte[]d=MessageDigest.getInstance("SHA-256").digest(v.getBytes(StandardCharsets.UTF_8));StringBuilder s=new StringBuilder();for(byte b:d)s.append(String.format(Locale.ROOT,"%02x",b&255));return s.toString();}catch(NoSuchAlgorithmException e){throw new IllegalStateException(e);}}
    private static boolean requiredSelector(Map<String,BlueprintSpecification>s){for(String k:List.of("REFERENCE","ARCHETYPE","CATEGORY")){BlueprintSpecification x=s.get(k);if(x!=null&&x.requirement()==BlueprintSpecification.Requirement.REQUIRED)return true;}return false;}
    private static Map<String,BlueprintSpecification> first(List<BlueprintSpecification>s){Map<String,BlueprintSpecification>m=new LinkedHashMap<>();for(BlueprintSpecification x:s)m.putIfAbsent(x.key(),x);return m;}
    private static String text(JsonObject o,String k){JsonElement e=o.get(k);if(e==null||e.isJsonNull())throw new IllegalStateException("Missing corpus field "+k);return e.getAsString();}
    private static int[] v3(JsonArray a){if(a==null||a.size()!=3)throw new IllegalStateException("Invalid corpus vector");return new int[]{a.get(0).getAsInt(),a.get(1).getAsInt(),a.get(2).getAsInt()};}
    private static String norm(String s){return s.trim().toUpperCase(Locale.ROOT).replace('-','_').replace(' ','_');}
    private static String clean(String s){return s.toLowerCase(Locale.ROOT).replace(':',' ').replace('/',' ').replace('_',' ').replace('-',' ').trim();}
    private static String slug(String s){int i=s.lastIndexOf('/');if(i>=0)return s.substring(i+1);i=s.lastIndexOf(':');return i>=0?s.substring(i+1):s;}
    private static boolean idMatches(String requested,String actual){return clean(requested).equals(clean(actual))||clean(slug(requested)).equals(clean(slug(actual)));}
    private static Set<String> tokens(String s){return new LinkedHashSet<>(Arrays.asList(clean(s).split("\\s+")));}

    private record Entry(String id,String kind,String category,String path,String status){}
    private record Index(String version,List<Entry> references,Map<String,Entry> byId){}
    private record Scored(Entry entry,int score){}
    private record Candidate(Entry entry,JsonObject ref,String refId,String archetype,String corporateId,Dims dims,String sizeClass,int score){}
    private record Dims(int w,int h,int d){}
    private record P(int x,int y,int z) implements Comparable<P>{public int compareTo(P q){int c=Integer.compare(x,q.x);if(c!=0)return c;c=Integer.compare(y,q.y);return c!=0?c:Integer.compare(z,q.z);}}
}
