import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.common.exceptions import NoSuchElementException
import pandas as pd



# Saisissez le sujet de recherche
sujet_recherche = input("Saisissez le sujet de recherche : ")

# Ouvrez le navigateur Chrome (assurez-vous d'avoir ChromeDriver installé)
driver = webdriver.Chrome()

# Accédez à Google Scholar
driver.get("https://scholar.google.com/")

# Trouvez la zone de saisie et saisissez le sujet de recherche
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys(sujet_recherche)
search_box.send_keys(Keys.RETURN)

# Attendez que les résultats de la recherche soient visibles
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "gs_res_ccl")))

# Create an empty DataFrame to store the data
data = []

# Récupérez les liens vers les profils des auteurs
author_links = driver.find_elements(By.CSS_SELECTOR, ".gs_a a")

# Boucle sur chaque lien d'auteur pour accéder à son profil
for index, link in enumerate(author_links):
    try:
        # Open the link in a new tab
        link.send_keys(Keys.CONTROL + Keys.RETURN)

        # Switch to the newly opened tab
        driver.switch_to.window(driver.window_handles[1])

        # Wait for the author's profile to be visible
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "gsc_prf_in")))

        # Récupérez le nom de l'auteur
        author_name = driver.find_element(By.CSS_SELECTOR, "#gsc_prf_in").text

        # Récupérez le profil
        author_info = driver.find_element(By.CSS_SELECTOR, ".gsc_prf_il").text

        # Récupérez les fields
        fields = driver.find_element(By.CSS_SELECTOR, "#gsc_prf_int").text

        # Récupérez les valeurs des barres du graphique
        chart_values = [int(value.text) for value in driver.find_elements(By.CSS_SELECTOR, ".gsc_g_xtl")]
        

        # Extraire les éléments
        #elements = driver.find_elements(By.CLASS_NAME, 'gsc_rsb_std')
        elements = driver.find_elements(By.CSS_SELECTOR, ".gsc_rsb_std")
        total_citations_toutes = elements[0].text
        total_citations_depuis2018 = elements[1].text
        h_index_toutes = elements[2].text
        h_index_depuis2018 = elements[3].text
        i_index_toutes = elements[4].text
        i_index_depuis2018 = elements[5].text

        # Récupérez les coauteurs
        coauthors = [coauthor.text for coauthor in driver.find_elements(By.CSS_SELECTOR, ".gsc_rsb_a_desc a")]

        # Wait for the articles to be present
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#gsc_prf_int")))

        # Récupérez les informations sur les articles
        article_titles = [title.text.strip() for title in driver.find_elements(By.CSS_SELECTOR, ".gsc_a_at")]

        article_authors_sources = driver.find_elements(By.CSS_SELECTOR, ".gs_gray")
        article_authors = [info.text.strip() for i, info in enumerate(article_authors_sources) if i % 2 == 0]
        article_sources = [info.text.strip() for i, info in enumerate(article_authors_sources) if i % 2 != 0]

        article_cited_by = [cited_by.text.strip() for cited_by in driver.find_elements(By.CSS_SELECTOR, ".gsc_a_c a")]
        article_published_in = [published_in.text.strip() for published_in in driver.find_elements(By.CSS_SELECTOR, "td.gsc_a_y span")]


        """years = [int(year.text) if year.text.strip() else 0 for year in
                 driver.find_elements(By.CSS_SELECTOR, ".gsc_g_t")]
        chart_values = [int(value.text) if value.text.strip() else 0 for value in
                        driver.find_elements(By.CSS_SELECTOR, ".gsc_g_xtl")]"""
        

        # Click on the chart to open the chart overlay if it's present
        """try:
            chart = driver.find_element(By.CSS_SELECTOR, ".gsc_md_hist_b")
            chart.click()

            # Wait for the chart overlay to be visible
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".gsc_md_hist_overlay")))

            # Extract the data from the chart overlay
            years = [year.text.strip() for year in driver.find_elements(By.CSS_SELECTOR, "div.gsc_md_hist_b span")]
            #print(years)

            cits = [cit.text.strip() for cit in driver.find_elements(By.CSS_SELECTOR, "a.gsc_g_a span")]
            print(cits)

            # Close the chart overlay
            close_button = driver.find_element(By.CSS_SELECTOR, "span.gs_ico")
            close_button.click()

        except NoSuchElementException:
            print("Chart element not found or accessible. Skipping chart interaction.")"""


        

    


        # Ajoutez les données à la liste
        data.append({
            #"Auteur": author_name,
            "Universite": author_info,
            #"Citations totales": total_citations_toutes,
            #"Total des citations Depuis 2018": total_citations_depuis2018,
            #"Indice h total": h_index_toutes,
            #"Indice h Depuis 2018": h_index_depuis2018,
            #"i-index Toutes": i_index_toutes,
            #"i-index Depuis 2018": i_index_depuis2018,
            #"Nombre de citations par an": chart_values,
            "Fields": fields,
            #"Coauthors": coauthors,
            #"Article Titles": article_titles,
            #"Article_authors": article_authors,
            #"Article_sources": article_sources,
            #"Article_cited_by": article_cited_by,
            #"Article_published_in": article_published_in
           
        })

        # Add a short delay before closing the current tab
        time.sleep(2)  # You can adjust the sleep duration as needed

    except StaleElementReferenceException:
        print("Stale element reference encountered. Retrying...")
        continue  # Skip to the next iteration

    except TimeoutException:
        print("Timeout exception. Retrying...")
        continue  # Skip to the next iteration

    except Exception as e:
        print(f"Erreur lors du traitement de l'auteur : {e}")

    finally:
        # Close the current tab and switch back to the main tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data)

# Export the DataFrame to an Excel file
df.to_excel("affcc.xlsx", index=False)

# Fermez le navigateur
driver.quit()
