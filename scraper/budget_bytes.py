import scrapy

from producer import get_producer, send_event


class BudgetBytesSpider(scrapy.Spider):
    name = 'Budget Bytes'
    start_urls = ['https://www.budgetbytes.com/category/recipes/']
    producer = get_producer()

    def parse(self, response):
        recipe = {'url': response.url}

        recipe['ingredients'] = []
        recipe['steps'] = []

        for ingredient_li in response.css('.wprm-recipe-ingredient'):
            recipe['ingredients'].append({
                'amount': ingredient_li.css('.wprm-recipe-ingredient-amount::text').get(),
                'unit': ingredient_li.css('.wprm-recipe-ingredient-unit::text').get(),
                'name': ingredient_li.css('.wprm-recipe-ingredient-name::text').get()
            })
            recipe['steps'] = [
                step.get()
                for step in response.css(
                    ".wprm-recipe-instructions .wprm-recipe-instruction-text span::text"
                )
            ]
            send_event(self.producer, recipe)

        for recipe_page in response.css('.post .more a'):
            yield response.follow(recipe_page, self.parse)

        for next_page in response.css('.nav-links a.next'):
            yield response.follow(next_page, self.parse)
