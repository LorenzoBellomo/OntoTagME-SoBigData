package rest.service;

import java.util.*;

public interface ICategoryService {
    void findAllCategories();
    List<String> getCategories(int wid);
}
