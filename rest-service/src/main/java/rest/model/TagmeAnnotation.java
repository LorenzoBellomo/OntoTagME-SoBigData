package rest.model;

import java.util.List;

public class TagmeAnnotation {
    private int    wid;
    private String spot;
    private String word;
    private String originWord;
    private int    startPos;
    private int    endPos;
    private float  rho;
    private String categories;

    public TagmeAnnotation(String topic, String rword, String originW, int start_pos, int end_pos, int wid, float rho, List<String> categories) {
        this.wid      = wid;
        this.spot     = rword;
        this.word     = topic;
        this.originWord = originW;
        this.startPos = start_pos;
        this.endPos   = end_pos;
        this.rho      = rho;
        this.categories_configuration(categories);
    }

    private void categories_configuration(List<String> categories) {
        this.categories = "";
        for(String category: categories)
            this.categories += "\"" + category  + "\",";
        this.categories = (!this.categories.equals("")) ?
                this.categories.substring(0, this.categories.length() - 1) : "\"\"";
    }

    @Override
    public String toString() {
        return "TagmeAnnotation{" +
                "wid=" + wid +
                ", spot='" + spot + '\'' +
                ", word='" + word + '\'' +
                ", originWord=" + originWord + '\'' +
                ", startPos=" + startPos +
                ", endPos=" + endPos +
                ", rho=" + rho +
                ", categories='" + categories + '\'' +
                '}';
    }

    public int    getWid() {
        return wid;
    }
    public String getSpot() {
        return spot;
    }
    public String getWord() {
        return word;
    }
    public int    getStartPos() {
        return startPos;
    }
    public int    getEndPos() {
        return endPos;
    }
    public float  getRho() {
        return rho;
    }
    public String getOriginWord() {return originWord;}
    public String getCategories() {
        return categories;
    }
}
