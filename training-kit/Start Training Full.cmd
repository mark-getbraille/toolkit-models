@echo off
rem Train the 4B model on up to three times as many pictures (about 110,000; roughly three days on a fast card).
call "%~dp0kit\run.cmd" --model 4b --size full
