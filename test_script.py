from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed

class FlipkartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup WebDriver
        cls.driver = webdriver.Chrome()  # Or use webdriver.Firefox() for Firefox
        cls.driver.get("https://www.flipkart.com")
        cls.driver.maximize_window()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        # Load test data from JSON file
        with open('test_data.json') as f:
            self.data = json.load(f)

    def close_login_popup(self):
        try:
            close_login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="✕"]'))
            )
            close_login_button.click()
        except Exception as e:
            print("No login popup found:", e)

    def test_login(self):
        driver = self.driver
        self.close_login_popup()

        try:
            # Click on login button if needed
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[text()="Login"]'))
            )
            login_button.click()

            # Enter username
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="text" and @name="username"]'))
            )
            username_field.send_keys(self.data['username'])

            # Enter password
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="password" and @name="password"]'))
            )
            password_field.send_keys(self.data['password'])

            # Click login button
            login_submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and @class="_2KpZ6l _2HKlqd _3AWRsL"]'))
            )
            login_submit_button.click()

            # Wait for login to complete
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a[@href="/account"]'))
            )
            print("Login successful")

        except Exception as e:
            print("Error during login test:", e)
            driver.get_screenshot_as_file("login_error.png")  # Take a screenshot for debugging

    def test_search_product(self):
        driver = self.driver
        self.close_login_popup()

        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'q'))
            )
            search_box.send_keys(self.data['search_product'])
            search_box.send_keys(Keys.RETURN)

            # Wait for search results to load
            results = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div._1AtVbE'))
            )
            self.assertGreater(len(results), 0, "No products found")
            print("Search product test passed")

        except Exception as e:
            print("Error during search product test:", e)
            driver.get_screenshot_as_file("search_product_error.png")  # Take a screenshot for debugging

    def test_add_to_cart(self):
        driver = self.driver
        self.test_search_product()  # Ensure search functionality is working

        try:
            # Click on the first product
            first_product = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div._1AtVbE a'))
            )
            first_product.click()

            # Click on "Add to Cart" button
            add_to_cart_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "_2KpZ6l") and contains(text(), "ADD TO CART")]'))
            )
            add_to_cart_button.click()

            # Verify item is added to cart
            cart_icon = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@href="/cart"]'))
            )
            cart_icon.click()

            cart_items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div._1AtVbE'))
            )
            self.assertGreater(len(cart_items), 0, "Cart is empty")
            print("Add to cart test passed")

        except Exception as e:
            print("Error during add to cart test:", e)
            driver.get_screenshot_as_file("add_to_cart_error.png")  # Take a screenshot for debugging

    def run_tests_concurrently(self):
        # Run tests concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.test_login): "login",
                executor.submit(self.test_search_product): "search_product",
                executor.submit(self.test_add_to_cart): "add_to_cart"
            }
            for future in as_completed(futures):
                test_name = futures[future]
                try:
                    future.result()
                    print(f"{test_name} completed successfully")
                except Exception as e:
                    print(f"{test_name} failed with exception: {e}")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(FlipkartTests)
    unittest.TextTestRunner().run(suite)
