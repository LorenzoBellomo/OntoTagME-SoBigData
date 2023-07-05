package rest.service;

import it.acubelab.tagme.AnnotatedText;
import it.acubelab.tagme.Annotation;
import it.acubelab.tagme.preprocessing.TopicSearcher;
import org.springframework.stereotype.Service;
import rest.model.TagmeAnnotation;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.io.*;


@Service
public class AnnotationPruningService {

    private boolean has2be_pruned(String real_word, String topic, float rho, boolean isDisambiguated, StopwordService sp) {
        boolean cond1 = !sp.isStopword(real_word) && !sp.isStopword(topic);
        boolean cond2 = rho >= 0.0;
        return  cond1 && cond2 && isDisambiguated;
    }


    public List<TagmeAnnotation> getTagmeAnnotation(
           List<Annotation> annotations,
           StopwordService  stopService,
           ICategoryService categoryService,
           AnnotatedText    annotatedText,
           TopicSearcher    searcher
    ) throws IOException {
        List<TagmeAnnotation> final_annotations = new LinkedList<>();
        for (Annotation annotation: annotations) {
            Annotation eq  = annotation.getEqual();
            Annotation sup = annotation.getSuperior();

            /* there is a parent because this annotation is contained into the parent */
            if (eq == null && sup != null)
                continue;

            int start_pos = annotatedText.getOriginalTextStart(annotation);
            int stop_pos  = annotatedText.getOriginalTextEnd(annotation);
            String originword = annotatedText.getOriginalText(annotation);   //
            if(eq != null && sup != null) {
                annotation = eq;
            }

            /* annotation parameter */
            float   rho        = annotation.getRho();
            int     wid        = annotation.getTopic();
            boolean isDisamb   = annotation.isDisambiguated();
            String  topic      = searcher.getTitle(annotation.getTopic());
            String  realWord   = annotatedText.getOriginalText(annotation);

            /* if there are index problem, topic and real word will be equal */
            if (topic == null)
                topic = realWord;
            List<String> categories   = categoryService.getCategories(wid);
            //List<Category> categories = categoryService.findByTitle(topic);
            boolean isAllLower = true;

            if (this.has2be_pruned(realWord, topic, rho, isDisamb, stopService) && isAllLower){
                TagmeAnnotation tagmeAnnot = new TagmeAnnotation(topic, realWord, originword, start_pos, stop_pos, wid, rho, categories);
                final_annotations.add(tagmeAnnot);
            }
        }
        return final_annotations;
    }

}
