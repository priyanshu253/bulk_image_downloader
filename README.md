# Mass Image Downloader
Download Multiple Google Images

**Requirements**
* Python 2.7 and above Version
* Lib: BeautifulSoup, requests, json etc.

**Install Lib**

        sudo apt update

        sudo apt install python-pip

        sudo pip install requests

        sudo apt-get install python-bs4

**Steps**

Step 1: Create download directory
        
        mkdir GoogleImages
        
Step 2: Check list of Params accepted
        
        python massImageDownloaderForGoogle.py --help
        
Step 3: Download Image
        
        python massImageDownloaderForGoogle.py --search "Priyanka Chopra" --num_images 20
        
Enjoy :)
