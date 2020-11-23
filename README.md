# webscraper
WEBSCRAPER (v1.0)

        COMMANDS
                scrape -  scrape data from a url or a html file 
                get    -  get structured data from a group
                dump   -  delete an existing group
                flush  -  delete all cached html files
                save   -  save a group or get a saved group
                quit   -  quit the program (exit also has the same function)
                clear  -  clears the terminal screen

        
        SYNOPSIS
                scrape {--url url | --html html_file_directory} -s starting_pattern -e ending_pattern [-n data_name] 
                       {[-g group_name] | [--pretty]} [--cache]

        DESCRIPTION
                scrape can be used to scrape out data using a website's url or html file in your local system. The 
                task is achieved through a query by providing various inputs (using flags) like starting_pattern,
                ending_pattern, url or html_file_directory. Other inputs include data_name, group_name.

                The scraping process is implemented using starting_pattern and ending_pattern. The data in interest 
                should be between starting_pattern and ending_pattern, like in the below example:
                    <div class="format"> ... data ... </div>
                In the above case,  <div class="format"> is the starting_pattern and  </div> is the ending_pattern. 
                This way the data in between is scraped out and this is implemented across the complete website code, 
                thus retriving all those data of similar kind.

                If no -g or --group is been used, then scrape will only print the output and won't store
                it in a group. In the other case, the data will be stored in the provided group (group_name) and no 
                output will be show. You will have to retrive the stored the data using get command.
            
                The options(/flags) are as follows:

                --url url
                            This option is used to specify the url. This is used to fetch the code  

                -s starting_pattern, --start starting_pattern
                            This option is used to specify the starting_pattern.       

                -e ending_pattern, --end ending_pattern
                            This option is used to specify the ending_pattern.
                
                -n data_name, --name data_name
                            In case there are multiple but similar type of data, like prices of a list of products, 
                            then this is used to specify the name of the type of data (data_name). It is used
                            as a key for the data in JSON format.


                -g group_name, --group group_name
                            A group is class storing the data collect from a source. It can hold more than one kind
                            of data, given that they are of the same sizes (like names and prices of products). The
                            program has a default group called default.  
                            
                            default is used for storing data if no group is provided. It's cleared after the 
                            output is printed. If you use default for group_name, then a warning is shown
                            asking, are you sure to use it. In such case, the output will not be printed and you have
                            to get the output using get.

                --pretty
                            Used to print the data in a pretty format. 

                --cache
                            HTML code of a webpage, from where the data was scraped, could be cached by using this 
                            option. scrape will first search if there is a cached code for the webpage, if there
                            isn't one then only it will send the GET request.  


        SYNOPSIS
                get group_name [--pretty]

        DESCRIPTION
                get is used to retrive structured data saved in a group, in a JSON format. A group is class storing 
                the data collect from a source.  It can hold more than one kind of data, given that they are of the same 
                sizes (like names and prices of products). The program has a default group called default.

                The options(/flags) are as follows:

                --pretty
                            Used to print the data in a pretty format. 


        SYNOPSIS
                dump group_name

        DESCRIPTION
                dump is used to delete an existing group

        
        SYNOPSIS
                save group_name [--name file_name | --get file_name] 
        
        DESCRIPTION
                save can be used to save data stored in a group in a .save file.

                The option(/flags) are as follows:
                
                --name file_name
                            Used to provide a name to the save file. If the file_name already exists, then it's name will be
                            automatically changed to file_name-(i), where i is a suitable integer. If this option(/flag) is
                            omitted then the name of file will be of the format group_name-sha_code, where sha_code
                            will be the SHA code of the data been saved.
                
                --get file_name
                            Used to get a saved file.       
