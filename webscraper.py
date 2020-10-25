from urllib.request import urlopen
import json
from colorIO import cprint
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
    data = data.split('\n')
    info_list = []
    for line in data:
        if pattern['start'] in line and pattern['end'] in line:
            line = line.strip()
            line = line[len(pattern['start']):(line.index(pattern['end']))]
            info_list.append(line)
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
def scrap_cmd(flags_list, groups):
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
            pass 
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
        save_file_location = '.saved/{}.save'.format(file_name)

    os.system('> {}'.format(save_file_location))
    if save_data is not None:
        with open(save_file_location, 'w') as save_file:
            save_file.write(save_data)
            save_file.close()
        if file_name is None:
            report('data saved by fetch code \'{}-{}\''.format(group_name ,sha512_encode(save_data)), 'done')
        else:
            report('data saved by name \'{}.save\''.format(file_name), 'error')
def get_save_file(file_name):
    try:
        with open('.saved/{}.save'.format(file_name),'r') as save_file:
            print(save_file.read())
            save_file.close()
    except FileNotFoundError:
        report('Error: file not found','error')

def main():
    groups = []
    groups.append({'group_name':'default', 'group': group('default')})

    while True:
        cmd = input('\n[webscraper] $ ')
        cmd, flags = parse_cmd(cmd)

        help_message = ''

        if cmd == 'help':
            print(help_message)
        elif cmd == 'scrap':
            scrap_cmd(flags, groups)
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