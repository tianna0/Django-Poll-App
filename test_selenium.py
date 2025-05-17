import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import string

BASE_URL = "http://127.0.0.1:8000"

def random_string(length=6):
    return ''.join(random.choices(string.ascii_letters, k=length))

class PollAppSeleniumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_1_register(self):
        driver = self.driver
        wait = self.wait
        driver.get(f"{BASE_URL}/accounts/register/")
        username = random_string()
        email = f"{username}@example.com"
        password = "Testpass123"

        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password1").send_keys(password)
        driver.find_element(By.NAME, "password2").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Redirect to login after success
        self.assertIn("/accounts/login", driver.current_url)

    def test_2_login(self):
        driver = self.driver
        wait = self.wait
        driver.get(f"{BASE_URL}/accounts/login/")
        driver.find_element(By.NAME, "username").send_keys("tian")
        driver.find_element(By.NAME, "password").send_keys("123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for Logout button to appear
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))
        self.assertIn("Logout", driver.page_source)

    
    def test_3_vote(self):
        driver = self.driver
        wait = self.wait
        driver.get(f"{BASE_URL}/polls/list/")

        poll_link = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//ul[@class='list-group']//a[contains(@href, '/polls/')]")
        ))
        poll_link.click()


        choices = wait.until(EC.presence_of_all_elements_located((By.NAME, "choice")))
        choices[0].click()

        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Vote']").click()


        page = driver.page_source
        self.assertTrue(
            "Results" in page or "Polls List" in page,
            "Expected to see results or be redirected to poll list, but didn't."
        )


    def test_4_create_poll_as_admin(self):
        driver = self.driver
        wait = self.wait

        driver.get(f"{BASE_URL}/polls/add/")

        question = "Is Selenium testing useful? " + random_string()
        wait.until(EC.presence_of_element_located((By.NAME, "text"))).send_keys(question)
        driver.find_element(By.NAME, "choice1").send_keys("Yes")
        driver.find_element(By.NAME, "choice2").send_keys("No")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        wait.until(EC.url_contains("/polls/list"))
        self.assertIn("/polls/list", driver.current_url)
    
    def test_5_edit_poll(self):
        driver = self.driver
        wait = self.wait
        driver.get(f"{BASE_URL}/polls/list/user/")
        

        edit_link = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//a[@title='Edit Poll']")
        ))
        driver.execute_script("arguments[0].click();", edit_link)


        updated_text = "Updated question " + random_string()
        textarea = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        textarea.clear()
        textarea.send_keys(updated_text)

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        wait.until(EC.url_contains("/polls/list"))
        self.assertIn("/polls/list", driver.current_url)
        self.assertIn(updated_text.split()[0], driver.page_source)
                


if __name__ == "__main__":
    unittest.main()
