@echo off
rem Train the 4B picture model on every permissive collection, normal size (needs an NVIDIA card with 12 GB or more).
call "%~dp0kit\run.cmd" --model 4b
