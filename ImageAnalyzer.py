from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import requests
import os
import argparse
import base64
import googleapiclient.discovery
import matplotlib.pyplot as plt
from collections import Counter

def download_images(url, download_folder="downloaded_images"):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Launch Selenium WebDriver to get dynamic contents of the web page
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(10)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    for img in soup.find_all('img', src=lambda x: x and x.startswith("https://cloudfront-us-east-2.images.arcpublishing.com/reuters")):
        src = img['src']
        try:
            response = requests.get(src, stream=True)
            if response.status_code == 200:
                filename = src.split('/')[-1].split("?")[0]
                image_path = os.path.join(download_folder, filename)
                with open(image_path, 'wb') as out_file:
                    out_file.write(response.content)
                print(f"Downloaded {image_path}")
        except requests.RequestException as e:
            print(f"Failed to download {src}: {e}")


def main():
    histo = {}
    service = googleapiclient.discovery.build('vision', 'v1')
    downloaded_images = 'C://Users//Dima//cloud-vision//downloaded_images' # Directory has to be changed according to your PC/OS
    for img in os.listdir(downloaded_images):
        photo = os.path.join(downloaded_images, img)
        with open(photo, 'rb') as image:
            image_content = base64.b64encode(image.read())
            service_request = service.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': image_content.decode('UTF-8')
                    },
                    'features': [{
                        'maxResults': 4,
                        'type': 'LABEL_DETECTION'
                    }]
                }]
            })
        response = service_request.execute()
        print("Results for image %s:" % photo)
        for result in response['responses'][0]['labelAnnotations']:
            print("%s - %.3f" % (result['description'], result['score']))
            if photo in histo:
                histo[photo].append(f'{result['description']} - {result['score']}')
            else:
                histo[photo] = [f'{result['description']} - {result['score']}']
        with open(photo, 'rb') as image:
            image_content = base64.b64encode(image.read())
            service_request = service.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': image_content.decode('UTF-8')
                    },
                    'features': [{
                        'maxResults': 1,
                        'type': 'LOGO_DETECTION'
                    }]
                }]
            })
        response = service_request.execute()
        try:
            for result in response['responses'][0]['logoAnnotations']:
                print("%s - %.3f" % (result['description'], result['score']))
                if photo in histo:
                    histo[photo].append(f'{result['description']} - {result['score']}')
                else:
                    histo[photo] = [f'{result['description']} - {result['score']}']
        except KeyError:    # This means no logo can be identified from the image
            pass
        with open(photo, 'rb') as image:
            image_content = base64.b64encode(image.read())
            service_request = service.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': image_content.decode('UTF-8')
                    },
                    'features': [{
                        'maxResults': 1,
                        'type': 'LANDMARK_DETECTION'
                    }]
                }]
            })
        response = service_request.execute()
        try:
            for result in response['responses'][0]['landmarkAnnotations']:
                print("%s - %.3f" % (result['description'], result['score']))
                if photo in histo:
                    histo[photo].append(f'{result['description']} - {result['score']}')
                else:
                    histo[photo] = [f'{result['description']} - {result['score']}']
        except KeyError:    # This means no landmark can be identified from the image
            pass
    return histo


def plot_histogram(histo):
    descriptions = []
    for key, values in histo.items():
        for value in values:
            description = value.split(' - ')[0]
            descriptions.append(description)

    description_counts = Counter(descriptions)
    sorted_descriptions = dict(sorted(description_counts.items(), key=lambda item: item[1], reverse=True))

    plt.figure(figsize=(20, 10))
    plt.bar(range(len(sorted_descriptions)), sorted_descriptions.values(), tick_label=list(sorted_descriptions.keys()))
    plt.xlabel('Description', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.title('Frequency of Descriptions in Images', fontsize=16)
    plt.xticks(rotation=90, fontsize=10)
    plt.xlim(-1, len(sorted_descriptions))
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.4, top=0.95)
    plt.savefig('description_frequency_histogram.png', bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='The website you\'d like to scrape for images and send them to Google Vision.')
    args = parser.parse_args()
    download_images(args.url)
    histo = main()
    plot_histogram(histo)
