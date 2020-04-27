#!/usr/bin/env python

from termcolor import colored

def print_container(title, container):
	print(colored(title, "red"))

	if len(container) != 0:
		for line in container:
			print(colored(line, "green"))
	else:
		print(colored("No items", "green"))
	return

def print_text(title, text):
	print(colored(title, "red"))

	if len(text) != 0:
		print(colored(text, "green"))
	else:
		print(colored("No items", "green"))
	return