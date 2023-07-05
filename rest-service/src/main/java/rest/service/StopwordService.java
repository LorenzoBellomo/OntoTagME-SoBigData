package rest.service;

import org.apache.commons.lang.StringUtils;
import org.springframework.stereotype.Service;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.Scanner;

@Service
public class StopwordService {
    public HashMap<String, Integer> stopwords;

    /*Stopwords extraction*/
    public void getStopwords(String path) {
        stopwords  = new HashMap<>();
        File myObj = new File(path);

        try {
            int counter      = 0;
            Scanner myReader = new Scanner(myObj);
            while (myReader.hasNextLine()) {
                String data  = myReader.nextLine();
                stopwords.put(data, counter++);
                stopwords.put(StringUtils.capitalize(data), counter++);
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    /*Check if the word is a stopword*/
    public boolean isStopword(String word) {
        return stopwords.containsKey(word);
    }
}
