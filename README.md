# Keyword_scraping

## Problem statement
In this project we want to scrape 3K + web sites. They do not have the same structure, but we want to get the same information from each of them if possible.

The information is:
* address
* phone numbers
* social media links
* yes / no flag for a list of key words. If the keyword is found on the page, the flag for this word should be yes.

In our case we want not only the main page to be scraped, but also a list of child pages to be scraped as well and results to be combined.

Given that the number of sites is huge, we want to make sure that we use parallelisation as much as possible.

## Solution

Used classes and their responsibilities:
### class Site
The class is responsbile for storing and representing information about a single page. It has the following public methods:
* fetch_site_content —> sends an http request to the site link and stores the page content inside the class.
* to_dict -> publid representation of the internal class methods. Ensures that each class has the same representation format
* run -> our site inherits from Thread to support multythreading computations.

Each site has a number of properties. I used caching to make sure that the actual calculations run only once. The properties are:
* site_soup. Is a local property. Contains result of convertion of the page_content into beautiful soup object.
* links. List of all links on the page
* self_links. List of links leading to the same site. This property is useful on the upper level calculations.

We also define a dunder `__add__` method to allow operations like:
```python
site_a = Site(...)
site_b = Site(...)
comnined_site = site_a + site_b
```

This method is widely used in the SiteGroup class described below.

### class SiteGroup

What we found during the project is that a lot of keyword-related information is stored outside of the main page. For example:
```
http://company_site.az/
http://company_site.az/about-us
http://company_site.az/our-mission
http://company_site.az/product-1
http://company_site.az/product-2
```

In this case when we want to scrape the `company_site` we also want to check child pages. So the site group is made exactly for this. It is responsible for
* processing the main page
* identifying list of child pages
* processing each child page
* combining the result

This site also inherits from `Thread` to support multithreading operations.

The class has only one public method `run` that realizes the following sequence of operations:
1. Create a Site object for the main page
2. Fetch and process the main page
3. Retrieve a list of child pages of the main site
4. Fetch each fetch and process each child page in a separate thread
5. Combine results into a common dictionary, once all chile pages have been fetched.

### scraping process
As I mentioned above, we want to parallelization as possible. So each chunk of pages is processed inside a single `process` of `muliprocessing` module. Inside each process main page is scraped and after all child pages are scraped within separate threads, which speeds up the whole process. Once preprocessing of the chunk is complete, resulting dataframe is stored in a separate `xlsx` file.

One fetching of all chunks is complete, the all chunk files are combied in a single output file.

The whole diagram looks like this:
```
Process1          : ------------------------------------->|
  site1           : -------------------->|
    main_page     : --------->|
      child_page1 :            ------->  |
      child_page2 :             -------> |
      child_page3 :              ------->|
  site2           : -------------------->|
    main_page     :   --------->|
      child_page1 :              ------->  |
      child_page2 :               -------> |
      child_page3 :                ------->|
...               :              ............   
  siten           :                 -------------------->|
    main_page     :                 --------->|
      child_page1 :                            ------->  |
      child_page2 :                             -------> |
      child_page3 :                              ------->|

```
