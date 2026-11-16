@echo off
rem Train the 4B model on every collection including Wikipedia: the add-on is then CC BY-SA 4.0. See READ ME FIRST.txt.
call "%~dp0kit\run.cmd" --model 4b --with-wikipedia
