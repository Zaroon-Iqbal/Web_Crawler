#Zaroon Iqbal ID:028902417
import networkx as nx
import matplotlib.pyplot as plt
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
import logging
from matplotlib.cm import ScalarMappable
import time

#global variable for storing the links and their edges
outBound = dict()
url_set = set()
graph = nx.DiGraph()#directed graph

class Crawler_link(CrawlSpider):
  name = "Crawler_link"
  allowed_domains = list()
  start_urls = list()

  #rules to help makesure the crawling is getting the correct links
  rules = ( 
    Rule(
      LinkExtractor(allow_domains= allowed_domains), callback = 'parse_links', follow = True)
    ,)
  #A pool of user agents so that can avoid being detected
  user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
        # Add more user agents as needed
    ]
  #custom settings to make sure not detected and get 429 error
  custom_settings = {
        'CONCURRENT_REQUESTS': 8,#to make sure too many requests aren't happening at once
        'DOWNLOAD_DELAY': 0.5,#delay to not get error
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [500, 429], #retry on these specific codes
    }
   
  
  #constructior used to initialize paramaters
  def __init__(self, file = None, outBound = None, url_set = None, *args, **kwargs, ):
    super(Crawler_link, self).__init__(*args, **kwargs)
    #opening and extracting urls from file
    File = open(file)
    lines = File.readlines()
    Main_domain = list()
    domain_list = []
    for line in lines:#loop through lines in txt file
        if "**" not in line:#stars wrap the urls
          domain = line.replace('\n', "")
          domain_list.append(domain)

    dom1 = domain_list.pop(0)#used as the domain page
    dom = dom1.replace('https://', "")
    dom = dom.replace("/", "")#these need to be out of the allowed domain list for scrapy
    Main_domain.append(dom)
    
    #initializing the domain, and start urls
    self.allowed_domains = Main_domain
    self.start_urls = domain_list
    self.dom1 = dom1
    self.outBound = outBound
    self.url_set = url_set
    value = int(input("Please input the maximum number of nodes:"))
    self.max = value
    self.Graph = graph


    #make sure that the crawler stops at the max number of nodes
    if getattr(self, 'max_iterations', None):
      self.crawler.settings.set('CLOSESPIDER_ITEMCOUNT', self.max)

  # parse method
  def parse_links(self, response):
    
    #user agent used to help not get detected
    user_agent = self.user_agents.pop(0)
    self.user_agents.append(user_agent)
    response.request.headers['User-Agent'] = user_agent

   #attempt to make the crawling pause when getting this error, 
    if response.status == 429:
       self.crawler.engine.pause()
       time.sleep(120)
       self.crawler.engine.unpause()

    #this is the parent node on each iteration
    parent = response.request.headers.get('referer', None).decode('utf-8')

    #make sure that there are still nodes to be created, this is to create a node in the set
    if self.max > len(self.url_set):
       if parent not in self.url_set:
         if parent not in self.outBound: # no duplicates can be done
            self.url_set.add(parent)
            self.outBound[parent] = set()#each new parent gets its own set

    #ensures that the responses are in the correct domain
    if response.url.find(self.dom1) == 0 and response.url is not parent: 
       
       #only create nodes when its less than the max
       if len(self.url_set) < self.max and response.url not in self.url_set:
          self.url_set.add(response.url)#creating new node
          self.outBound[response.url] = set() #add to dictionary for future possible edges
          self.outBound[parent].add(response.url)

       #only adds an edge to the dictionaries when its lesss than the max nodes wanted
       elif len(self.url_set) <= self.max and response.url in self.url_set:
          self.outBound[parent].add(response.url)

    
    #to finish creating the edges for the response.url nodes
    if response.url in self.url_set:
       exiting_links = response.css('a::attr(href)').extract()

       #only have links that have the domain name
       for link in exiting_links:
          if link.find(self.dom1) == 0:
             if link is not response.url:#make sure not a duplicate
               self.outBound[response.url].add(link)#added to the set and finalize the dictionary of nodes and edges

    #closing the crawler when reaching the max        
    if self.max == len(self.url_set):
       self.crawler.engine.close_spider(self, "Reached maximum number of links")

choice = '0'
graph_status = 0 #to check if a graph is made

#Menu options for this particular assignment
while choice != '6':
    print("\nPlease choose one of the following options")
    print("1. Crawl through websites and create a directed graph given the file of URLs ")
    print("2. Save the graph.")
    print("3. Upload a graph.")
    print("4. Print The LogLog Plot of the graph that was created.")
    print("5. Perform the PageRank Algorithm.")
    print("6. Exit.")

    choice = input("What is your choice?")

    if choice == '1':
       #file = input("Please enter the name/path of the file ex(C:Users\game.txt) (using 2 \) :\n")#need to do \\ slashes for path to work

       file = "C:\\Users\\zaroo\\Documents\\GitHub\\Assignment-5-Web-Crawler-\\sample.txt" #can be used to hardcode file in

       process = CrawlerProcess()
       process.crawl(Crawler_link, file, outBound, url_set)
       process.start()
       #disable matplog debug messages
       logging.getLogger('matplotlib.font_manager').disabled = True
       logging.getLogger('matplotlib.ticker').disabled = True

       #creating the graph of nodes and edges from the dictionaries
       for node in outBound:
          #if actually part of node set
          if node in url_set:
             #all outgoing links per node
             for out in outBound[node]:  
               #if the node exists           
               if out in url_set and node is not out:
                    graph.add_edge(node, out)
                    
       #creating and displaying the graph
       pos = nx.spring_layout(graph)
       nx.draw(graph, pos, with_labels = True)
       plt.show()
       graph_status = 1

    elif choice == '2':
       #saving the file
       if graph_status == 1:
        name = input("Please input the name of the (.graphml) file you would like to save without the extension:")
        nx.write_graphml(graph, name + ".graphml")
       else:
          print("There is no graph to save please upload (option 3) or run option 1!!")

    elif choice == '3':
       #uploading a file 
       namee = input("Please input the name of the file you would like to upload without the extension(Must be graphml):")
       graph = nx.read_graphml(namee + ".graphml")
       pos1 = nx.spring_layout(graph)
       nx.draw(graph, pos1, with_labels = True)
       plt.show()
       graph_status = 1

    elif choice == '4':
       if graph_status == 1:
      
        inDegree = dict(graph.in_degree())# dictionary of all nodes indegrees

        plt.loglog(list(inDegree.values()), linestyle='-')#creating loglog plot
        plt.title('Log-Log Plot of In-Degrees')
        plt.show()
       else:
          print("There is no graph to save please upload (option 3) or run option 1!!")

    elif choice == '5':
       if graph_status == 1:
        iterations = int(input("How many iterations of PageRank?:"))
        pagerank = nx.pagerank(graph, max_iter=iterations)
        #printing the pageranks to console to see what values are given
        for n, p in pagerank.items():
          print(n, "pagerank:", p)

        subgraph = graph.copy()#creating a copy to make a sub graph of the original
        value1 = float(input("Please enter the first integer value range:"))
        value2 = float(input("Please enter the second integer value range:"))

         #only keeping the nodes that are within the desired range
        for node in graph.nodes():
          rank = pagerank.get(node)
          if rank < value1 or rank > value2:#removing values greater than the upper or lower than the lower bound
              subgraph.remove_node(node)

        node_size = [5000 * pagerank[node] for node in subgraph.nodes()]#increase the size of the nodes based on pagerank
        node_color = [pagerank[node] for node in subgraph.nodes()]

        pos = nx.spring_layout(subgraph)
        
        cmap = plt.cm.Blues
        bar = ScalarMappable(cmap=cmap)
        bar.set_array([0,1])#the set range of values to map color to
        nx.draw(subgraph, pos, node_size=node_size, node_color=node_color, cmap=cmap)
        plt.colorbar(bar, label='Pagerank')
        plt.show()
        
        #creating a txt file of the pageranks of all nodes
        with open ("PageRank.txt", 'w') as file:
          for node, rank in pagerank.items():
            file.write(f"Node {node}: PageRank = {rank}\n")

        
       else:
          print("There is no graph to save please upload (option 3) or run option 1!!")


    elif choice == '6':
       pass
       break
