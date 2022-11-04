
-- pcall(os.execute, "git clone git@github.com:kompasim/my-build-tools.git ./.my-build-tools")
-- package.path = package.path .. ";./.my-build-tools/?.lua"
package.path = package.path .. ";../../?.lua"
local Builder = require("c_builder")

local builder = Builder(false)
builder:setInput('./client.c')
builder:setLibs("dyad")
builder:setOutput('client')
builder:start(false)

local builder = Builder(false)
builder:setInput('./server.c')
builder:setLibs("dyad")
builder:setOutput('server')
builder:start(false)

os.execute("Start " .. files.csd() .. "./server.exe")
os.execute("Start " .. files.csd() .. "./client.exe")