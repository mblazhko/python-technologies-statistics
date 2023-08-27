from urllib.parse import urljoin
import scrapy


DJINNI_EMAIL = "vifidov384@xgh6.com"
DJINNI_PASS = "qwerty_12345"


class DjinniSpider(scrapy.Spider):
    name = "djinni"
    allowed_domains = ["djinni.co"]
    start_urls = [
        "https://djinni.co/",
    ]

    def start_requests(self):
        login_url = "https://djinni.co/login"
        yield scrapy.Request(login_url, callback=self.login)

    def login(self, response):
        csrf_token = response.css(
            'input[name="csrfmiddlewaretoken"]::attr(value)').get()
        yield scrapy.FormRequest.from_response(
            response,
            formdata={
                "csrfmiddlewaretoken": csrf_token,
                "email": DJINNI_EMAIL,
                "password": DJINNI_PASS
            },
            callback=self.after_login
        )

    def after_login(self, response):
        if "Welcome" in response.text:
            self.logger.info("Logged in successfully!")
            yield scrapy.Request(
                url="https://djinni.co/jobs/?all-keywords=&any-of-keywords=&exclude-keywords=&primary_keyword=Python",
                callback=self.parse
            )
        else:
            self.logger.error("Login failed!")

    def parse(self, response):
        job_items = response.css(".list-jobs .job-list-item")
        for job in job_items:
            job_url = job.css(".job-list-item__link::attr(href)").get()
            detailed_url = urljoin(response.url, job_url)
            yield scrapy.Request(
                detailed_url, callback=self.parse_one_job
            )

    def parse_one_job(self, response):
        yield {
            "title": response.css(
                "h1::text"
            ).get().strip(),
            "required-experience": response.css(
                '.job-additional-info--body '
                '.job-additional-info--item '
                '.job-additional-info--item-text:contains("experience")::text'
                ).get().strip(),
            "technologies": response.css(
                '.job-additional-info--item-text span.text-gray-600::text'
            ).getall(),
        }
