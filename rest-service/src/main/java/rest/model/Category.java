package rest.model;

import java.util.List;

public class Category {

    private String pageTitle;

    private Integer tagmeId;

    private List<String> categories;

    private String id;

    public Category() {
    }

    public Category(String pageTitle, List<String> categories, String id) {
        this.pageTitle = pageTitle;
        this.categories = categories;
        this.id = id;
    }

    public Integer getTagmeId() {
        return tagmeId;
    }

    public void setTagmeId(Integer tagmeId) {
        this.tagmeId = tagmeId;
    }

    public String getPageTitle() {
        return pageTitle;
    }

    public void setPageTitle(String pageTitle) {
        this.pageTitle = pageTitle;
    }

    public List<String> getCategories() {
        return categories;
    }

    public void setCategories(List<String> categories) {
        this.categories = categories;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

}
