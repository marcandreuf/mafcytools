#! /usr/bin/python3

import subprocess
import sys
import socket
import shutil
import os
import pprint
import tarfile

# It is required to do a free registration and create a license key
LICENSE_KEY = 'add your key here'
# docs: https://dev.maxmind.com/geoip/geoip2/geolite2/
GEO_LITE_TAR_FILE_URL = f'https://download.maxmind.com/app/geoip_download' \
                        f'?edition_id=GeoLite2-City' \
                        f'&license_key={LICENSE_KEY}' \
                        f'&suffix=tar.gz'
DB_DIR = './GeoIP'
DB_FNAME = '/GeoLite2-City.mmdb'
DB_ZIP_FNAME = '/GeoIP2LiteCity.tar.gz'


def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])


try:
    import maxminddb
    import requests
except ImportError:
    print('[!] Failed to Import maxminddb or requests')
    try:
        pygeoip_choice = input('[*] Attempt to Auto-install_package imports? [y/N]')
    except KeyboardInterrupt:
        print('\n [!] User Interrupted Choice')
        sys.exit(1)

    if pygeoip_choice.strip().lower()[0] == 'y':
        print('[*] Attempting to Install imports...')
        sys.stdout.flush()
        try:
            import pip
            install_package('requests')
            install_package('geoip2')
            install_package('maxminddb')

            import maxminddb
            import requests
            print('[DONE]')
        except Exception as e:
            print('[FAIL]', e)
            sys.exit(1)
    elif pygeoip_choice.strip().lower()[0] == 'n':
        print('[*] User Denied Auto-install_package')
        sys.exit(1)
    else:
        print('[!] Invalid Decision')
        sys.exit(1)


class Locator:

    def __init__(self, url=None, ip=None, data_file=None):
        self.url = url
        self.ip = ip
        self.data_file = data_file
        self.target = ''

    def check_database(self):
        if not self.data_file:
            self.data_file = DB_DIR + DB_FNAME
        else:
            if not os.path.isfile(self.data_file):
                print('[!] Failed to Detect Specified Database')
                sys.exit(1)
            else:
                return

        if not os.path.isfile(self.data_file):
            print('[!] Default Database Detection Failed')
            try:
                database_choice = input('[*] Attempt to Auto-install_package Database? [y/N]')
            except KeyboardInterrupt:
                print('\n [!] User Interrupted Choice')
                sys.exit(1)

            if database_choice.strip().lower()[0] == 'y':
                print('[*] Attempting to Auto-install_package Database... ')
                sys.stdout.flush()
                if not os.path.isdir(DB_DIR):
                    os.makedirs(DB_DIR)
                try:
                    url = GEO_LITE_TAR_FILE_URL
                    response = requests.get(url)

                    with open(DB_DIR + DB_ZIP_FNAME, 'wb') as f:
                        f.write(response.content)
                        f.flush()

                except Exception as ex:
                    print('[FAIL]', ex)
                    print('[!] Failed to Download Database')
                    sys.exit(1)

                try:
                    my_tar = tarfile.open(DB_DIR + DB_ZIP_FNAME)
                    extract_file = [name for name in my_tar.getnames() if 'mmdb' in name][0]
                    my_tar.extract(extract_file, DB_DIR)
                    my_tar.close()
                    os.remove(DB_DIR + DB_ZIP_FNAME)
                    shutil.move(DB_DIR + '/' + extract_file, DB_DIR + DB_FNAME)
                except IOError as ioe:
                    print('[FAIL]', ioe)
                    print('[!] Failed to Decompress Database')
                    sys.exit(1)

                print('[DONE]\n')
            elif database_choice.strip().lower()[0] == 'n':
                print('[!] User Denied Auto-Install')
                sys.exit(1)
            else:
                print('[!] Invalid Choice')
                sys.exit(1)

    def query(self):
        if self.url is not None:
            print(f"[*] Translating {self.url}")
            sys.stdout.flush()
            try:
                self.target += socket.gethostbyname(self.url)
                print(self.target)
            except Exception as ex:
                print('\n[!] Failed to Resolve URL', ex)
                return
        else:
            self.target += self.ip

        try:
            print(f'[*] Querying for Records of {self.target}')

            with maxminddb.open_database(self.data_file) as reader:
                data = reader.get(self.target)
                pprint.pprint(data)
                print('\n[*] Query Complete!')
        except Exception as ex:
            print('\n[!] Failed to Retrieve Records', ex)
            return


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='IP Geolocation Tool')
    parser.add_argument('--url', help='Locate an IP based on a URL',
                        action='store', default=None, dest='url')
    parser.add_argument('-t', '--target', help='Locate the specified IP',
                        action='store', default=None, dest='ip')
    parser.add_argument('--dat', help='Custom databaase filepath',
                        action='store', default=None, dest='datafile')
    args = parser.parse_args()

    print(f'args: {args}')

    if ((args.url is not None and args.ip is not None) or
            (args.url is None and args.ip is None)):
        parser.error('invalid target specification')

    try:
        locate = Locator(url=args.url, ip=args.ip, data_file=args.datafile)
        locate.check_database()
        locate.query()
    except Exception as e:
        print('\n[!] An Unknown Error Occurred', e)
