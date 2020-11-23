from urllib.request import urlopen
import json
from colorIO import cprint, colored
import time
import os
from SHA512 import sha512_encode

class group:
    def __init__(self, group_name):
        self.group_name = group_name
        self.patterns = {
            'name': [],
            'pattern': []
        }
        self.info = []
    def add(self, name, pattern,info_list):
        self.patterns['name'].append(name)
        self.patterns['pattern'].append(pattern)
        self.info.append(info_list)
    def dump(self):
        self.patterns = {
            'name': [],
            'pattern': []
        }
        self.info = []

def get_data(url):
    report('Fetching cached data', 'in_progress')
    html = cache(url, 'read')
    if html is None:
        try:
            report('No cached data found', 'error')
            report('Sending GET Request', 'in_progress')
            html = urlopen(url).read()
            report('Found URL\n  Received data', 'done')
            time.sleep(0.5)
            return html.decode('utf-8')
        except:
            report('Error: invalid url', 'error')
    else:
        report('Found cached data', 'done')
        return html
def scrape_info(data, pattern):
    if data is None:
        return ''
    data_portion = data
    info_list = []
    while True:
        try:
            start_pattern_index = data_portion.index(pattern['start'])
            data_portion = data_portion[start_pattern_index:]
            start_pattern_index = 0
            info_end_index = data_portion.index(pattern['end'])
            info_start_index = len(pattern['start'])
            end_pattern_index = info_end_index + len(pattern['end'])
            info = data_portion[info_start_index:info_end_index]
            info = info.strip()
            if info[0] == '\n':
                info.pop(0)
            if info[-1] == '\n':
                info.pop(-1)
            info_list.append(info)
            data_portion = data_portion[end_pattern_index:]
        except:
            return info_list
    return info_list
def organized_data(group):
    patterns = group.patterns
    info = group.info
    organized_data = {}
    if info != []:
        for i in range(len(info[0])):
            dic = {}
            for j in range(len(patterns['name'])):
                dic[patterns['name'][j]] = info[j][i]
            organized_data[i] = dic
    return organized_data
def get(cmd, groups):
    cmd = cmd.split()
    if len(cmd) > 3:
        report('Error: invalid query', 'error')
        return None
    group_name = cmd[1]
    output_format = cmd[2:]

    if output_format == []:
        output_format = '--raw'
    else:
        output_format = output_format[0]

    group_exists = False
    if group_name[0] != '-':
        for i in range(len(groups)):
            if group_name == groups[i]['group_name']:
                current_group = groups[i]['group']
                output_data = str(organized_data(current_group))
                group_exists = True
                break
        if group_exists:
            if output_format == '--raw':
                return output_data
            elif output_format == '--pretty':
                return json_pretty_print(eval(output_data))
        else:
            report('Error: no group named \'{}\' exists'.format(group_name), 'error')
            return None
    else:
        report('Error: no group name provided', 'error')
        return None
def parse_cmd(cmd):
    cmd = cmd.split(' -')
    command = cmd[0].strip()
    flags = []
    for tag in cmd [1:]:
        try:
            index_of_first_space = tag.index(' ')
        except:
            index_of_first_space = len(tag)
        flags.append({
            'flag': '-' + tag[:index_of_first_space],
            'input': tag[index_of_first_space+1:]
        })
    return command, flags
def scrape_cmd(flags_list, groups):
    flags = []
    input_val = []
    confirmation = True
    for flag in flags_list:
        flags.append(flag['flag'])
        input_val.append(flag['input'])
    
    if '--url' in flags:
        url = input_val[flags.index('--url')]
    elif '--html' in flags:
        html = input_val[flags.index('--html')]
        url = None
    else:
        url = None
        html = None
        
    if '-n' in flags:
        pattern_name = input_val[flags.index('-n')]
    elif '--name' in flags:
        pattern_name = input_val[flags.index('--name')]
    else: 
        pattern_name = None

    if '-s' in flags:
        start_pattern = input_val[flags.index('-s')]
    elif '--start' in flags:
        start_pattern = input_val[flags.index('--start')]
    else:
        report('Error: no starting pattern flag was provided (-s or --start)', 'error')
        confirmation = False

    if '-e' in flags:
        end_pattern = input_val[flags.index('-e')]
    elif '--end' in flags:
        end_pattern = input_val[flags.index('--end')]
    else:
        report('Error: no ending pattern flag was provided (-e or --end)', 'error')
        confirmation = False

    if '-g' in flags:
        group_name = input_val[flags.index('-g')]
        if group_name == 'default':
            yn = input('Warning: \'default\' is a reserved group used by webscraper.\nDo you still want to use it anyway(y/n): ')
            if yn != 'y'and yn != 'Y':
                confirmation = False

    elif '--group' in flags:
        group_name = input_val[flags.index('--group')]
        if group_name == 'default':
            yn = input('Warning: \'default\' is a reserved group used by webscraper.\nDo you still want to use it anyway(y/n): ')
            if yn != 'y'or yn != 'Y':
                confirmation = False
    else:
        group_name = 'default'

    if '--pretty' in flags:
        output_format = '--pretty'
    else: 
        output_format = ''
    
    cache_code = False
    if '--cache' in flags:
        cache_code = True

    if confirmation == True:
        group_exists = does_group_exists(group_name,groups)
        if not group_exists:
            groups.append({'group_name':group_name, 'group': group(group_name)})
        
        pattern = {
            'start': start_pattern,
            'end': end_pattern
        }

        data = None
        if url != None:
            data = get_data(url)
            if cache_code == True:
                cache(url, 'write', data)
            info = scrape_info(data, pattern)
        elif html != None:
            html = r'{}'.format(html)
            with open(html, 'r') as html:
                data = html.read()
                html.close()
            info = scrape_info(data, pattern)
            

        else:
            report('Error: no link is provided (check if you used --url or --html)', 'error')

        if data is not None:
            if '-g' not in flags and '--group' not in flags:
                groups[0]['group'].add(pattern_name, pattern, info)
                print(get('get default '+output_format ,groups))
                groups[0]['group'].dump()
            else:
                for i in range(len(groups)):
                    if group_name == groups[i]['group_name']:
                        current_group = groups[i]['group']
                        break
                current_group.add(pattern_name, pattern, info)
                report('Scraped information has been added to group \'{}\''.format(current_group.group_name), 'done')
    else:
        print('')
def does_group_exists(group_name, groups):
    group_exists = False
    for i in range(len(groups)):
        if groups[i]['group_name'] == group_name:
            group_exists = True
    return group_exists
def dump_group(cmd, groups):
    group_name = cmd.replace('dump ','').strip()
    group_exists = does_group_exists(group_name,groups)
    if group_exists:
        for i in range(len(groups)):
            if group_name == groups[i]['group_name']:
                groups[i]['group'].dump()
                break
    else:
        report('Error: no group named \'{}\' exists'.format(group_name), 'error')
def json_pretty_print(dic):
    return json.dumps(dic, indent=4)
def report(message, m_type):
    if m_type == 'error':
        cprint(message, 'red')
    elif m_type == 'done':
        cprint(message, 'green')
    elif m_type == 'in_progress':
        cprint(message, 'yellow')
def cache(url, action, code = ''):
    if '.codecache' not in os.listdir():
        os.system('mkdir .codecache')
    url = sha512_encode(url)
    if action == 'write':
        if '{}.cache'.format(url) not in os.listdir('.codecache'):
            os.system('> .codecache/{}.cache'.format(url))
            with open('.codecache/{}.cache'.format(url), 'w') as cache:
                cache.write(code)
                cache.close()
            
    elif action == 'read':
        try:
            with open('.codecache/{}.cache'.format(url), 'r') as cache:
                code = cache.read()
                cache.close()
            return code
        except FileNotFoundError:
            return None
def flush(cmd):
    cmd = cmd.strip().split()
    if len(cmd) > 2:
        report('Error: invalid query', 'error')
        return None
    if cmd[1] == 'all':
        os.system('rm .codecache/*')
        report('all cache has been cleared', 'done')
    else:
        cache_sha = sha512_encode(cmd[1])
        if '{}.cache'.format(cache_sha) in os.listdir('.codecache'):
            os.system('rm .codecache/{}.cache'.format(cache_sha))
            report('cache from url \'{}\' has been removed', 'done')
        else:
            report('no cache from url \'{}\' exists', 'error')
def save(group_name, file_name, groups):
    save_data = get('get {} --pretty'.format(group_name), groups)
    if '.saved' not in os.listdir():
        os.system('mkdir .saved')
    if file_name is None:
        save_file_location = '.saved/{}-{}.save'.format(group_name, sha512_encode(save_data))
    else:
        i = 1
        file_name_changed =False
        while file_name in os.listdir('.saved'):
            save_file_location = '.saved/{}-({}).save'.format(file_name, str(i))
            i += 1
            file_name_changed = True
        else:
            save_file_location = '.saved/{}.save'.format(file_name)
        file_name = save_file_location.replace('.saved/', '').replace('.save', '')
            

    os.system('> {}'.format(save_file_location))
    if save_data is not None:
        with open(save_file_location, 'w') as save_file:
            save_file.write(save_data)
            save_file.close()
        if file_name is None:
            report('data saved by fetch code \'{}-{}\''.format(group_name ,sha512_encode(save_data)), 'done')
        else:
            if file_name_changed:
                report('file named \'{}\' already exists'.format(file_name), 'error')
            report('data saved by name \'{}.save\''.format(file_name), 'done')
def get_save_file(file_name):
    try:
        with open('.saved/{}.save'.format(file_name),'r') as save_file:
            print(save_file.read())
            save_file.close()
    except FileNotFoundError:
        report('Error: file not found','error')
def help_message():
    help_message = '''
        {bold_underline_WEBSCRAPER} (v1.0)

        {bold_COMMANDS}
                {bold_scrape} -  scrape data from a url or a html file 
                {bold_get}    -  get structured data from a group
                {bold_dump}   -  delete an existing group
                {bold_flush}  -  delete all cached html files
                {bold_save}   -  save a group or get a saved group
                {bold_quit}   -  quit the program ({bold_exit} also has the same function)
                {bold_clear}  -  clears the terminal screen

        
        {bold_SYNOPSIS}
                {bold_scrape} {opening_curly_braces}{bold_url_flag} {underline_webpage_url} | {bold_html_flag} {underline_html_file_directory}{closing_curly_braces} {bold_s_flag} {underline_starting_pattern} {bold_e_flag} {underline_ending_pattern} [{bold_n_flag} {underline_data_name}] 
                       {opening_curly_braces}[{bold_g_flag} {underline_group_name}] | [{bold_pretty_flag}]{closing_curly_braces} [{bold_cache_flag}]

        {bold_DESCRIPTION}
                {bold_scrape} can be used to scrape out data using a website's url or html file in your local system. The 
                task is achieved through a query by providing various inputs (using flags) like {underline_starting_pattern},
                {underline_ending_pattern}, {underline_webpage_url} or {underline_html_file_directory}. Other inputs include {underline_data_name}, {underline_group_name}.

                The scraping process is implemented using {underline_starting_pattern} and {underline_ending_pattern}. The data in interest 
                should be between {underline_starting_pattern} and {underline_ending_pattern}, like in the below example:
                    <div class="format"> ... data ... </div>
                In the above case,  <div class="format"> is the {underline_starting_pattern} and  </div> is the {underline_ending_pattern}. 
                This way the data in between is scraped out and this is implemented across the complete website code, 
                thus retriving all those data of similar kind.

                If no {bold_g_flag} or {bold_group_flag} is been used, then {bold_scrape} will only print the output and won't store
                it in a group. In the other case, the data will be stored in the provided group ({underline_group_name}) and no 
                output will be show. You will have to retrive the stored the data using {bold_get} command.
            
                The options(/flags) are as follows:

                {bold_url_flag} {underline_webpage_url}
                            This option is used to specify the {underline_webpage_url}. This is used to fetch the code  

                {bold_s_flag} {underline_starting_pattern}, {bold_start_flag} {underline_starting_pattern}
                            This option is used to specify the {underline_starting_pattern}.       

                {bold_e_flag} {underline_ending_pattern}, {bold_end_flag} {underline_ending_pattern}
                            This option is used to specify the {underline_ending_pattern}.
                
                {bold_n_flag} {underline_data_name}, {bold_name_flag} {underline_data_name}
                            In case there are multiple but similar type of data, like prices of a list of products, 
                            then this is used to specify the name of the type of data ({underline_data_name}). It is used
                            as a key for the data in JSON format.


                {bold_g_flag} {underline_group_name}, {bold_group_flag} {underline_group_name}
                            A group is class storing the data collect from a source. It can hold more than one kind
                            of data, given that they are of the same sizes (like names and prices of products). The
                            program has a default group called {underline_default}.  
                            
                            {underline_default} is used for storing data if no group is provided. It's cleared after the 
                            output is printed. If you use {underline_default} for {underline_group_name}, then a warning is shown
                            asking, are you sure to use it. In such case, the output will not be printed and you have
                            to get the output using {bold_get}.

                {bold_pretty_flag}
                            Used to print the data in a pretty format. 

                {bold_cache_flag}
                            HTML code of a webpage, from where the data was scraped, could be cached by using this 
                            option. {bold_scrape} will first search if there is a cached code for the webpage, if there
                            isn't one then only it will send the GET request.  


        {bold_SYNOPSIS}
                {bold_get} {underline_group_name} [{bold_pretty_flag}]

        {bold_DESCRIPTION}
                {bold_get} is used to retrive structured data saved in a group, in a JSON format. A group is class storing 
                the data collect from a source.  It can hold more than one kind of data, given that they are of the same 
                sizes (like names and prices of products). The program has a default group called {underline_default}.

                The options(/flags) are as follows:

                {bold_pretty_flag}
                            Used to print the data in a pretty format. 


        {bold_SYNOPSIS}
                {bold_dump} {underline_group_name}

        {bold_DESCRIPTION}
                {bold_dump} is used to delete an existing group

        
        {bold_SYNOPSIS}
                {bold_save} {underline_group_name} [{bold_name_flag} {underline_file_name} | {bold_get_flag} {underline_file_name}] 
        
        {bold_DESCRIPTION}
                {bold_save} can be used to save data stored in a group in a .save file.

                The option(/flags) are as follows:
                
                {bold_name_flag} {underline_file_name}
                            Used to provide a name to the save file. If the {underline_file_name} already exists, then it's name will be
                            automatically changed to {underline_file_name}-({underline_i}), where {underline_i} is a suitable integer. If this option(/flag) is
                            omitted then the name of file will be of the format {underline_group_name}-{underline_sha_code}, where {underline_sha_code}
                            will be the SHA code of the data been saved.
                
                {bold_get_flag} {underline_file_name}
                            Used to get a saved file.       
        '''.format(
            opening_curly_braces = '{',
            closing_curly_braces = '}',
            bold_underline_WEBSCRAPER = colored('WEBSCRAPER' , bold=True, underline=True),
            bold_COMMANDS = colored('COMMANDS', bold=True),
            bold_DESCRIPTION = colored('DESCRIPTION', bold=True),
            bold_SYNOPSIS = colored('SYNOPSIS', bold=True),
            bold_scrape = colored('scrape', bold=True),
            bold_get = colored('get', bold=True),
            bold_dump = colored('dump', bold=True),
            bold_flush = colored('flush', bold=True),
            bold_save = colored('save', bold=True),
            bold_quit = colored('quit', bold=True),
            bold_exit = colored('exit', bold=True),
            bold_clear = colored('clear', bold=True),
            bold_url_flag = colored('--url', bold=True),
            bold_html_flag = colored('--html', bold=True),
            bold_s_flag = colored('-s', bold=True),
            bold_start_flag = colored('--start', bold=True),
            bold_e_flag = colored('-e', bold=True),
            bold_end_flag = colored('--end', bold=True),
            bold_n_flag = colored('-n', bold=True),
            bold_name_flag = colored('--name', bold=True),
            bold_g_flag = colored('-g', bold=True),
            bold_group_flag = colored('--group', bold=True),
            bold_pretty_flag = colored('--pretty', bold=True),
            bold_cache_flag = colored('--cache', bold=True),
            bold_get_flag = colored('--get', bold=True),
            underline_starting_pattern = colored('starting_pattern', underline=True),
            underline_ending_pattern = colored('ending_pattern', underline=True),
            underline_webpage_url = colored('url', underline='url'),
            underline_html_file_directory = colored('html_file_directory', underline=True),
            underline_data_name = colored('data_name', underline=True),
            underline_group_name = colored('group_name', underline=True),
            underline_pretty_output = colored('pretty_output', underline=True),
            underline_i = colored('i', underline=True),
            underline_sha_code = colored('sha_code', underline=True),
            underline_default = colored('default', underline=True),
            underline_file_name = colored('file_name', underline=True)
        )

    return help_message

def main():
    groups = []
    groups.append({'group_name':'default', 'group': group('default')})

    while True:
        cmd = input('\n[webscraper] $ ')
        cmd, flags = parse_cmd(cmd)

        if cmd == 'help':
            print(help_message())
        elif cmd == 'scrape':
            scrape_cmd(flags, groups)
        elif 'get ' in cmd:
            if flags == []:
                flags.append({'flag':''})
            flag = flags[0]
            if (data := get('{} {}'.format(cmd, flag['flag']), groups)) is not None:
                print(data)
        elif 'dump ' in cmd:
            dump_group(cmd, groups)
            report('group \'{}\' has been dumped'.format(cmd.replace('dump ', '')), 'done')
        elif 'flush ' in cmd:
            flush(cmd)
        elif 'save' in cmd:
            group_name = cmd.replace('save ','')
            file_name = None
            if flags != []:
                for flag in flags:
                    file_name = flag['input']
                    if '--name' == flag['flag']:
                        save(group_name, file_name, groups)
                        break
                    if '--get' == flag['flag']:
                        get_save_file(file_name)  
            else:
                save(group_name, file_name, groups)
        elif cmd == 'quit' or cmd == 'exit':
            break
        elif cmd == 'clear':
            os.system('clear')
        else:
            report('Error: invalid query', 'error')

main()  