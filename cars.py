#!/usr/bin/env python3

import json
import locale
import sys
from reports import generate
import emails


def load_data(filename):
  """Loads the contents of filename as a JSON file."""
  with open(filename) as json_file:
    data = json.load(json_file)
  return data


def format_car(car):
  """Given a car dictionary, returns a nicely formatted name."""
  return "{} {} ({})".format(
      car["car_make"], car["car_model"], car["car_year"])


def process_data(data):
  """Analyzes the data, looking for maximums.

  Returns a list of lines that summarize the information.
  """
  max_revenue = {"revenue": 0}
  max_sales={"total_sales":0}
  count_by_year={}
  for item in data:
    # Calculate the revenue generated by this model (price * total_sales)
    # We need to convert the price from "$1234.56" to 1234.56
    item_price = locale.atof(item["price"].strip("$"))
    item_revenue = item["total_sales"] * item_price
    if item_revenue > max_revenue["revenue"]:
      item["revenue"] = item_revenue
      max_revenue = item

    # also handle max sales
    if item['total_sales']>max_sales["total_sales"]:
      max_sales=item

    # also handle most popular car_year
    if item['car']['car_year'] in count_by_year.keys():
      count_by_year[item['car']['car_year']]+=1
    else:
      count_by_year[item['car']['car_year']]=1

  temp=sorted(count_by_year.items(),key=lambda year:year[1],reverse=True)[0]

  summary = [
    f"The {max_revenue['car']} generated the most revenue: ${max_revenue['revenue']}.",
      f"The {max_sales['car']['car_model']} had the most sales: {max_sales['total_sales']}",
      f"The most popular year was {temp[0]} with {temp[1]} sales."
      ]

  return summary


def cars_dict_to_table(car_data):
  """Turns the data in car_data into a list of lists."""
  table_data = [["ID", "Car", "Price", "Total Sales"]]
  for item in car_data:
    table_data.append([item["id"], 
                      format_car(item["car"]), 
                      item["price"], 
                      item["total_sales"]]
                      )
  return table_data


def main(argv):
  """Process the JSON data and generate a full report out of it."""
  data = load_data("car_sales.json")
  summary = process_data(data)
  summary_for_pdf='<br/>'.join(summary)
  summary_for_mail='\n'.join(summary)
  #turn this into a PDF report
  generate('cars.pdf', 
          'Sales summary for last month',
          summary_for_pdf, 
          cars_dict_to_table(data)
          )
  #send the PDF report as an email attachment
  a=emails.generate('automation@example.com',
          'student-01-3a8b3396944a@example.com',
          'Sales summary for last month'
          ,summary_for_mail,'cars.pdf')
  # emails.send(a)
 


if __name__ == "__main__":
  main(sys.argv)
