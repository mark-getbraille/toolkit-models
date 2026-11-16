@echo off
rem A follow-up: carry on from the last finished 4B training with only the collections it did not have (a few hours).
call "%~dp0kit\run.cmd" --model 4b --continue
