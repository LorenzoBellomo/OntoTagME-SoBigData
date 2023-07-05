package rest;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.CrossOrigin;
import java.io.IOException;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import it.acubelab.tagme.AnnotatedText;
import it.acubelab.tagme.Annotation;
import it.acubelab.tagme.Disambiguator;
import it.acubelab.tagme.RelatednessMeasure;
import it.acubelab.tagme.RhoMeasure;
import it.acubelab.tagme.Segmentation;
import it.acubelab.tagme.TagmeParser;
import it.acubelab.tagme.config.TagmeConfig;
import it.acubelab.tagme.preprocessing.TopicSearcher;
import rest.model.TagmeAnnotation;
import rest.service.AnnotationPruningService;
import rest.service.ICategoryService;
import rest.service.StopwordService;


@RestController
public class TagmeStringController {

    private final ICategoryService categService;
    private final StopwordService stopwordService;
    private final AnnotationPruningService annotationPruningService;

	public TagmeStringController(ICategoryService categService, StopwordService stopwordService, AnnotationPruningService aPrunServ) {
		this.categService    = categService;
		this.stopwordService = stopwordService;
		this.stopwordService.getStopwords("stopwords/stop_words_english.txt");
		this.annotationPruningService = aPrunServ;
	}


	@CrossOrigin(origins="*")
    @RequestMapping(value="/tagme_string_legacy", produces="application/json")
	public String tagmeStringLegacy(@RequestParam(value="name", defaultValue="") String name) {
          TagmeConfig.init();
          String lang = "en";
          AnnotatedText ann_text = new AnnotatedText(name);
          RelatednessMeasure rel = RelatednessMeasure.create(lang);
          String result = "{ \"response\": [\n";

          try {
              TagmeParser parser        = new TagmeParser(lang, true);
              Disambiguator disamb      = new Disambiguator(lang);
              Segmentation segmentation = new Segmentation();
              RhoMeasure rho            = new RhoMeasure();
              parser.parse(ann_text);
              segmentation.segment(ann_text);
              disamb.disambiguate(ann_text, rel);
              rho.calc(ann_text, rel);

              List<Annotation> annots   = ann_text.getAnnotations();
              TopicSearcher    searcher = new TopicSearcher(lang);
              List<TagmeAnnotation> final_annots = annotationPruningService
                  .getTagmeAnnotation(annots, stopwordService, categService, ann_text, searcher);

              for (TagmeAnnotation annot: final_annots) {
                  result += "{" +
                      "\"wid\":  \""       + annot.getWid()                                                                + "\",\n" +
                      "\"spot\": \""       + annot.getSpot().replace("\'","'").replace("\\'","'").replace("\"", "'")       + "\",\n" +
                      "\"rho\":  \""       + annot.getRho()                                                                + "\",\n" +
                      "\"Word\": \""       + annot.getWord().replace("\'","'").replace("\\'","'").replace("\"", "'")       + "\",\n" +
                      "\"originWord\": \"" + annot.getOriginWord().replace("\'","'").replace("\\'","'").replace("\"", "'") + "\",\n" +
                      "\"categories\": ["  + annot.getCategories()                                                         + "],\n"  +
                      "\"start_pos\": "    + annot.getStartPos()                                                           + ",\n"   +
                      "\"end_pos\": "      + annot.getEndPos()                                                             + "\n"    +
                      "},";
              }
          } catch (IOException e) {System.out.println("Exception");}

          result = result.substring(0, result.length()-1); // remove useless comma
          result +="\n]}";
          return result;
    }

    @CrossOrigin(origins="*")
    @RequestMapping(value="/tagme_string", produces="application/json")
	public String tagmeString(@RequestParam(value="name", defaultValue="") String name) {
          TagmeConfig.init();
          String lang = "en";
          RelatednessMeasure rel = RelatednessMeasure.create(lang);
          String result = "{ \"response\": [\n";
          int prev_length = 0;
          Pattern re = Pattern.compile("[^.!?\\s][^.!?]*(?:[.!?](?!['\"]?\\s|$)[^.!?]*)*[.!?]?['\"]?(?=\\s|$)", Pattern.MULTILINE | Pattern.COMMENTS);
          Matcher reMatcher = re.matcher(name);
          int toAdd = 0;
          while (reMatcher.find()) {
            String text = reMatcher.group();
            AnnotatedText ann_text = new AnnotatedText(text);

            try {
                TagmeParser parser        = new TagmeParser(lang, true);
                Disambiguator disamb      = new Disambiguator(lang);
                Segmentation segmentation = new Segmentation();
                RhoMeasure rho            = new RhoMeasure();
                parser.parse(ann_text);
                segmentation.segment(ann_text);
                disamb.disambiguate(ann_text, rel);
                rho.calc(ann_text, rel);

                List<Annotation> annots   = ann_text.getAnnotations();
                TopicSearcher    searcher = new TopicSearcher(lang);
                List<TagmeAnnotation> final_annots = annotationPruningService
                    .getTagmeAnnotation(annots, stopwordService, categService, ann_text, searcher);

                for (TagmeAnnotation annot: final_annots) {
                    result += "{" +
                        "\"wid\":  \""       + annot.getWid()                                                                + "\",\n" +
                        "\"spot\": \""       + annot.getSpot().replace("\'","'").replace("\\'","'").replace("\"", "'")       + "\",\n" +
                        "\"rho\":  \""       + annot.getRho()                                                                + "\",\n" +
                        "\"Word\": \""       + annot.getWord().replace("\'","'").replace("\\'","'").replace("\"", "'")       + "\",\n" +
                        "\"originWord\": \"" + annot.getOriginWord().replace("\'","'").replace("\\'","'").replace("\"", "'") + "\",\n" +
                        "\"categories\": ["  + annot.getCategories()                                                         + "],\n"  +
                        "\"start_pos\": "    + (annot.getStartPos() + prev_length + toAdd)                                   + ",\n"   +
                        "\"end_pos\": "      + (annot.getEndPos() + prev_length + toAdd)                                     + "\n"    +
                        "},";
                }
                prev_length += text.length();
                toAdd++;
            } catch (IOException e) {System.out.println("Exception");}
          }

          result = result.substring(0, result.length()-1); // remove useless comma
          result +="\n]}";
          return result;
    }

    @CrossOrigin(origins="*")
    @RequestMapping(value="/category", produces="application/json")
    public String categoryTest(@RequestParam(value="wid", defaultValue="") String wid) {
        String result = "{ \"response\": [ ";
	    List<String> s = categService.getCategories(Integer.parseInt(wid));
	    for (String i : s) result += i + ",";
	    result = result.substring(0, result.length() - 1);
	    result += " ] }";
        return result;
    }
}
