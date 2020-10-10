import socket
import mysql.connector as sql

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

def get_data(hostname, url):
    s = socket.socket()
    s.connect(socket.gethostbyname(hostname), 80)
    s.send(str.encode('GET {} HTTP/1.1'.format(url)))
    data = ''
    while data_packet := s.recv(65536):
        data += data_packet
    data = data.decode('utf-8')
    return data
def scrape_info(data, pattern):
    data = data.spilt('\n')
    info_list = []
    for line in data:
        if pattern['start'] in line:
            line = line[len(pattern['start']):(len(line) - len(pattern['end']))]
            info_list.append(line)
    return info_list
def organized_data(group):
    patterns = group.patterns
    info = group.info
    organized_data = {}
    for i in range(len(info[0])):
        for j in range(len(patterns['name'])):
            organized_data[i][patterns['name'][j]] = info[j][i]
    return organized_data
def save_data_into_database(data, database, tablename):
    recursion_counter = 0
    try:
        db = sql.connect(host='localhost', user='root',passwd='jerin@2002SQL',auth_plugin='mysql_native_password')
    except ConnectionError as err:
        print('{}\nDatabase is not online'.format(err))
        recursion_counter += 1
        if recursion_counter < 15:
            print('Retry {}...'.format(str(recursion_counter)))
            save_data_into_database(data,database,tablename)
        else:
            print('Try again later')
    cursor = db.cursor()
    databases = cursor.execute('show databases;') 

    if database == None:
        cursor.execute('create database webscraper if not exists;')
        cursor.execute('use webscaper;')
    else:
        cursor.execute('create database {} if not exists;'.format(database))
    
    cursor.execute('create table {tablename}( ')
    for key in data.keys():
        cursor.execute()
def get(cmd, groups):
    cmd = cmd.split()
    if len(cmd) > 3:
        print('Error: Invalid commad')
    group_name = cmd[1]
    output_format = cmd[2:]

    if output_format == []:
        output_format = '--raw'
    else:
        output_format = output_format[0]

    if group_name[0] != '-':
        output_data = organized_data(groups[groups.index(group_name)])
        if output_format == '--raw':
            print(output_data)
    
    else:
        print('Error: no group name provided')

def main():
    while True:
        groups = []
        groups.append({'group_name':'default', 'group': group('default')})

        cmd = input('\nwebscraper$ ')
        if cmd.strip() == 'help':
            print('')
        elif 'scrap ' in cmd:
            cmd = cmd.split()
            if '--url' in cmd:
                if len(cmd) > cmd.index('--url')+1 :
                    url = cmd[cmd.index('--url')+1]
                    if url[0] == '-':
                        print('Error: no url provided')
                    else:
                        try:
                            hostname = url.split('/')[2]
                        except:
                            print('Error: not a valid url')
                            continue
                        
                        try:
                            if '-n' in cmd:
                                pattern_name = cmd[cmd.index('-n')+1]
                            elif '--pattern-name' in cmd:
                                pattern_name = cmd[cmd.index('--pattern-name')+1]
                            else: 
                                pattern_name = None
                        except:
                            print('Error: no pattern name was provided')
                            continue

                        try:
                            if '-s' in cmd:
                                start_pattern = cmd[cmd.index('-s')+1]
                            elif '--start' in cmd:
                                start_pattern = cmd[cmd.index('--start')+1]
                            else:
                                print('Error: no starting pattern flag was provided (-s or --start)')
                                continue
                        except:
                            print('Error: no starting pattern was provided')
                            continue
                        try:
                            if '-e' in cmd:
                                end_pattern = cmd[cmd.index('-e')+1]
                            elif '--end' in cmd:
                                end_pattern = cmd[cmd.index('--end')+1]
                            else:
                                print('Error: no ending pattern flag was provided (-e or --end)')
                                continue
                        except:
                            print('Error: no ending pattern was provided')
                            continue
                        try:
                            if '-g' in cmd:
                                group_name = cmd[cmd.index('-g')+1]
                                group_exists = False
                                if group_name == 'default':
                                    print('Error: you can\'t use \'default\' as a group name')
                                for i in range(len(groups)):
                                    if groups[i]['group_name'] == group_name:
                                        group_exists = True
                                if not group_exists:
                                    groups.append({'group_name':group_name, 'group': group(group_name)})
                            elif '--group' in cmd:
                                group_name = cmd[cmd.index('--group')+1]
                                group_exists = False
                                for i in range(len(groups)):
                                    if groups[i]['group_name'] == group_name:
                                        group_exists = True
                                if not group_exists:
                                    groups.append({'group_name':group_name, 'group': group(group_name)})
                                

                        except:
                            print('Error: no group name was provided')
                            continue

                        pattern = {
                            'start': start_pattern,
                            'end': end_pattern
                        }

                        if '-g' or '--group' not in cmd:
                            data = get_data(hostname, url)  
                            info = scrape_info(data, pattern)
                            groups[0].add(pattern_name, pattern, info)
                            get('get default',groups)
                        else:
                            data = get_data(hostname, url)  
                            info = scrape_info(data, pattern)
                            for i in range(len(groups)):
                                if group_name == groups[i]['name']:
                                    current_group = groups[i]['group']
                                    break
                            current_group.add(pattern_name, pattern, info)
                else:
                    print('Error: no url provided')
            else:
                print('Error: no --url flag provided')
        elif 'get' in  cmd:
            get(cmd, groups)
                