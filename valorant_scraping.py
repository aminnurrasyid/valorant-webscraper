from bs4 import BeautifulSoup
import pandas as pd
import requests

def bio_formatter(column, element):
    if column == "Appearances":
        if element.lower() == "valorant":
            return element.upper()
    elif column == "Voice Actor":
        return element.strip('[1]')
    elif column == "Affiliation(s)":
        temp_string1 = element.split()[0].lower() 
        if temp_string1 == "valorant":
            temp_string1 = temp_string1.upper()
            temp_string2 = " ".join(element.split()[1:])
            return temp_string1 + " " + temp_string2
        else:
            return element
    else:
        return element

def ability_formatter(ability_type, creds ):
    if ability_type == "Ultimate":
        return (creds.text).split()[-2] #avoid printing diamond because encoding issue
    elif creds != None:
        creds_f = (creds.text).strip("Cost: ")
        if creds_f == "Free":
            creds_f = 0
        elif isinstance(creds_f, str):
            creds_f = creds_f.split()[0]
        return creds_f 
    else:   # creds == None
        return creds

#declaring up main BeautifulSoup Object
html_text = requests.get('https://valorant.fandom.com/wiki/Agents').text
soup = BeautifulSoup(html_text, 'lxml')
#creating main dataframe
column_list = ['name', 'role', 'Aliases', 'Real Name', 'Origin', 'Race', 'Gender', 'Affiliation(s)', 'Appearances', 'Voice Actor', 'Passive1', 'Passive2', 'Basic1', 'Basic2','Basic3', 'Signature1', 'Signature2', 'Ultimate', 'Basic1_creds', 'Basic2_creds','Basic3_creds', 'Signature1_creds', 'Signature2_creds', 'Ultimate_points']
df_mainpage = pd.DataFrame(columns=column_list)

index_df = 0
agents = soup.find('table', class_="wikitable").find('tbody').find_all('tr')
for agent in agents[1:]:
    postlink = agent.a['href']
    link = 'https://valorant.fandom.com' + postlink

    #main-page scraping
    name = agent.select('td')[1].text.replace("\n", '')
    role = agent.select('td')[2].text.replace("\n", '')

    mainpage_list={'name':name,'role':role}
    df_mainpage = df_mainpage.append(mainpage_list, ignore_index=True)

    #agent-specific-page scraping
    agenthtml_text = requests.get(link).text
    agent_soup = BeautifulSoup(agenthtml_text, 'lxml')


    sections = agent_soup.find_all('section', class_='pi-item pi-group pi-border-color pi-collapse pi-collapse-open')
    for section in sections:
        #skipping in-game details section
        if (section.find('h2', class_="pi-item pi-header pi-secondary-font pi-item-spacing pi-secondary-background").text) == "Game Details":
            continue
    
        agentdetails = section.find_all('div', class_='pi-item pi-data pi-item-spacing pi-border-color')
        for agentdetail in agentdetails:
            col_ref = agentdetail.find('h3', class_='pi-data-label pi-secondary-font').text
            element = agentdetail.find('div', class_='pi-data-value pi-font').text
         
            #skip released date because of inconsistency of format
            if col_ref == "Added":
                continue
         
            element = bio_formatter(col_ref,element)
            df_mainpage.at[index_df,col_ref] = element  #assigning to specific cell in df


    abilities = agent_soup.find_all('div', class_="ability")
    passive_iter,basic_iter,signature_iter = 1,1,1
    for ability in abilities:
        ability_type = ability.findPreviousSibling('h3').text
        skillname = ability.find('a').text
        creds = ability.find('p', class_='details').find('span', class_='cost mobile-label')

        creds_value = ability_formatter(ability_type, creds) 

        if ability_type == "Passive":
            ability_col = ability_type + str(passive_iter)
            passive_iter+=1
            df_mainpage.at[index_df, ability_col] = skillname
            continue
        elif ability_type == "Basic":
            ability_col = ability_type + str(basic_iter)
            cost_col = ability_col + "_creds"
            basic_iter+=1
        elif ability_type == "Signature":
            ability_col = ability_type + str(signature_iter)
            cost_col = ability_col + "_creds"
            signature_iter+=1
        else:   #condition for ultimate
            ability_col = ability_type
            cost_col = ability_col + "_points"

        df_mainpage.at[index_df, ability_col] = skillname
        df_mainpage.at[index_df, cost_col] = creds_value
        
    index_df+=1


#improve column naming conventions
df_mainpage.rename(columns= {'Aliases':'alias', 'Real Name':'real_name', 'Origin':'origin', 'Race':'race', 'Gender':'gender', 'Affiliation(s)':'affiliation', 'Appearances':'appearances', 'Voice Actor':'voice_actor', 'Passive1':'passive1', 'Passive2':'passive2', 'Basic1':'basic1', 'Basic2':'basic2','Basic3':'basic3', 'Signature1':'signature1', 'Signature2':'signature2', 'Ultimate':'ultimate', 'Basic1_creds':'basic1_creds', 'Basic2_creds':'basic2_creds','Basic3_creds':'basic3_creds', 'Signature1_creds':'signature1_creds', 'Signature2_creds':'signature2_creds', 'Ultimate_points':'ultimate_points'},inplace=True)

df_mainpage.to_csv("./Data Science/Web Scraping/valorant_agent.csv", index=False)