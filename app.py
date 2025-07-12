from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_doctors():
    url = 'https://www.doctorbangladesh.com/doctors/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup.prettify()[:1000])  # Print the first 1000 chars of the HTML

    doctors = [] 
    for article in soup.select('article.post.entry'):
        header = article.select_one('header.entry-header')
        if not header:
            continue

        name_tag = header.select_one('h2.entry-title a')
        name = name_tag.text.strip() if name_tag else None
        link = name_tag['href'] if name_tag else None

        degree_tag = header.select_one('ul li[title="Degree"]')
        degree = degree_tag.text.strip() if degree_tag else None

        speciality_tag = header.select_one('li.speciality')
        speciality = speciality_tag.text.strip() if speciality_tag else None

        designation_tag = header.select_one('li[title="Designation"] strong')
        designation = designation_tag.text.strip() if designation_tag else None

        workplace_tag = header.select_one('li[title="Workplace"]')
        workplace = workplace_tag.text.strip() if workplace_tag else None

        img_tag = header.select_one('.photo img')
        img_url = img_tag['src'] if img_tag else None

        doctors.append({
            'name': name,
            'link': link,
            'degree': degree,
            'speciality': speciality,
            'designation': designation,
            'workplace': workplace,
            'photo': img_url
        })
    return doctors

@app.route('/api/doctors', methods=['GET'])
def api_doctors():
    data = get_doctors()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)