#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

from flask import Flask, request
import os
import telebot
import config
import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials

class Spreadsheet():

	def __init__(self):
		"""Доступ и авторизация в google sheets api"""
		self.scope= ['https://spreadsheets.google.com/feeds',
		        'https://www.googleapis.com/auth/drive']
		self.creds=ServiceAccountCredentials.from_json_keyfile_name('secret.json', self.scope)    
		self.client=gspread.authorize(self.creds)
		self.sheet=self.client.open('Library').sheet1    

	def check_bookname(self, data):
		"""Поиск по названию книги"""
		cnt=0
		row=0
		foundbook=''
		"""col_values(1) вместо 1 нужно написать номер столбца где будут храниться названия книг"""
		for bookname in self.sheet.col_values(2):  
			row=row+1
			if data.lower() in bookname.lower():
				cnt=cnt+1
				# "self.sheet.cell(row,2).value" вот таких строк нужно добавить сколько нужно
				# и вместо 2 нужно писать номер столбцов которые должен будет видеть юзер
				foundbook=foundbook+'\n'+bookname+' '+self.sheet.cell(row,1).value +' '+self.sheet.cell(row,2).value +' '+self.sheet.cell(row,3).value +' '+self.sheet.cell(row,4).value +' '+self.sheet.cell(row,5).value +' '+self.sheet.cell(row,6).value +' '+self.sheet.cell(row,7).value +' '+self.sheet.cell(row,9).value +' '+self.sheet.cell(row,13).value +' '+self.sheet.cell(row,19).value + ';'+'\n\n\n\n'
		if cnt==1:
		    return "Найдена только одна книга: "+foundbook
		elif cnt!=0:
			return "Есть несколько книг по названию "+data+':\n'+foundbook+"\nЕсть ли в списке книга которую вы искали? Мы рады вам помочь!"
		return "Наверное этой книги у нас нет. Попробуйте еще раз"

	def check_authname(self, data):
		"""Поиск по автору, здесь те же настройки как и в check_bookname()"""
		cnt=0
		row=0
		foundbook=''
		for auth_fullname in self.sheet.col_values(1):
			row=row+1
			if data.lower() in auth_fullname.lower():
				cnt=cnt+1
				foundbook=foundbook+'\n'+self.sheet.cell(row,2).value+' '+auth_fullname + ';'
		if cnt==1:
		    return "Найдена только одна книга: "+foundbook
		elif cnt!=0:
			return "Есть несколько книг по автору "+data+':\n'+foundbook+"\nЕсть ли в списке книга которую вы искали? Мы рады вам помочь!"
		return "Наверное этой книги у нас нет. Попробуйте еще раз."


	def check_fullname(self, data):
		"""Поиск по 'Книга' Имя Фамилия, здесь те же настройки как и в check_bookname()"""
		cnt=0
		row=0
		foundbook=''
		for bookname in self.sheet.col_values(1):
			row=row+1
			book=bookname+' '+self.sheet.cell(row,2).value
			if data.lower() in book.lower():
				cnt=cnt+1
				foundbook=foundbook+'\n'+book+';'
		if cnt==1:
		    return "У нас в наличии есть: "+foundbook
		elif cnt!=0:
			return "У нас в наличии несколько книг по этим данным \""+data+'\":\n'+foundbook+"\nЕсть ли в списке книга которую вы искали? Мы рады вам помочь!"
		return "Наверное этой книги у нас нет. Пожалуйста, попробуйте еще раз."

sheet1=Spreadsheet()

bot = telebot.TeleBot(config.token)

"""Стартовое, приветсвенное сообщение"""
@bot.message_handler(commands=['start', 'help'])
def handle_help_start(message):
    bot.send_message(message.chat.id, "Что-то про библиотеку.\nЕсли хотите проверить наличие какой либо книги, можете кликнуть на эти команды:\n\
    /book_name для того что бы искать по названию книги;\n\
    /authors_fullname по имени и фамилии автора;\n\
    /find_book по примеру: \"Книга\" Имя Фамилия.")

#Обработчик команды /book_name
@bot.message_handler(commands=['book_name'])
def check_book(message):
    bot.send_message(message.chat.id, "Напишите мне название книги которую хотите проверить на наличие. Пример: \"Маленький Принц\".")
    bot.register_next_step_handler(message, get_bookname)

def get_bookname(message):
	"""Отправляет сообщение(res) боту"""
	bookname = message.text
	res=sheet1.check_bookname(bookname)
	bot.send_message(message.from_user.id, res)

#Обработчик команды /authors_fullname
@bot.message_handler(commands=['authors_fullname'])
def check_auth(message):
    bot.send_message(message.chat.id, "Имя и фамилия автора книги которую хотите проверить на наличие. Пример: Мухтар Ауезов.")
    bot.register_next_step_handler(message, get_auth_name)

def get_auth_name(message):
	"""Отправляет сообщение(res) боту"""
	auth_name = message.text
	res=sheet1.check_authname(auth_name)
	bot.send_message(message.from_user.id, res)

#Обработчик команды /find_book
@bot.message_handler(commands=['find_book'])                                                                                   
def check_full(message):
    bot.send_message(message.chat.id, "Имя, фамилия автора и название книги которую хотите проверить на наличие.\nПример:\"Абай жолы\" Мухтар Ауезов.")
    bot.register_next_step_handler(message, get_full_name)

def get_full_name(message):
	"""Отправляет сообщение(res) боту"""
	full_name = message.text
	res=sheet1.check_fullname(full_name)
	bot.send_message(message.from_user.id, res)

#Обработчик для не правильных вводов
@bot.message_handler(content_types=['text'])
def check_error_msg(message):
    bot.send_message(message.chat.id, "Вы не ввели никакой команды, пожалуйста, кликните на /help что бы посмотреть список комманд.")


if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)
    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read())])
        return "!", 200
    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url="https://konaevalibrarybot.herokuapp.com/") # этот url нужно заменить на url вашего Хероку приложения
        return "?", 200
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
else:
	bot.remove_webhook()
	bot.polling(none_stop=True)
