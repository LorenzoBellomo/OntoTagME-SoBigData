package rest.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.PropertySource;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;
import rest.model.Category;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.FileNotFoundException;

import java.util.*;

@Service
@PropertySource(value = "classpath:application.properties")
public class CategoryService implements ICategoryService {

    @Autowired
    private Environment env;
    private HashMap<Integer, List<String>> categories;

    public CategoryService() {
        this.findAllCategories();
    }

    public void findAllCategories() {
        this.categories = new HashMap<>();
        try {
            try (BufferedReader TSVReader = new BufferedReader(new FileReader("/opt/multi-tagme-master_final/converters/tagme_category.csv"))) {
                String line = null;
                while ((line = TSVReader.readLine()) != null) {
                    String[] lineItems = line.split("\t");
                    List<String> cats = new ArrayList<String>();
                    String[] tmpCats = lineItems[2].split(";");
                    for (String s : tmpCats) {
                        if (!s.equals("NO TITLE")) {
                            cats.add(s);
                        }
                    }
                    Category doc = new Category(lineItems[0], cats, lineItems[1]);
                    doc.setTagmeId(Integer.parseInt(lineItems[1]));
                    categories.put(doc.getTagmeId(), doc.getCategories());
                }
            }
        } catch (IOException ioe) {
            ioe.printStackTrace();
        }
    }


    public List<String> getCategories(int wid) {
        return this.categories.getOrDefault(wid, new LinkedList<>());
    }

}
