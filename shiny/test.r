library(httr)
library(xml2)

getKillCount <- function(characterID, month){
  raw.data <- GET(paste("https://zkillboard.com/api/stats/characterID/", characterID, '/', sep = ''),
                  add_headers('Accept-Encoding' = 'gzip',
                              'User-Agent' = 'https://pleaseignore.com Maintainer: CogVokan@pleaseignore.com'))
  rd <- content(raw.data)
  nkills = rd$months[[month]]$shipsDestroyed
  
  if (is.null(nkills)){
    nkills <- 0
  }
  return(nkills)
}

getCharacterID <- function(character.name){
  character.name <- gsub(' ', '%20', character.name)
  raw.data <- GET(paste("https://api.eveonline.com/eve/CharacterID.xml.aspx?names=", character.name, sep = ''))
  main.xml = content(raw.data)
  result <- xml_child(main.xml, 'result')
  rowset <- xml_child(result, 'rowset')
  row <- xml_child(rowset, 'row')
  characterID <- xml_attr(row, 'characterID')

  return(characterID)
}

getCorpName <- function(characterID){
  raw.data <- GET(paste("https://api.eveonline.com/eve/CharacterInfo.xml.aspx?characterID=", characterID, sep = ''))
  main.xml = content(raw.data)
  result <- xml_child(main.xml, 'result')
  corpName <- xml_attr(result, 'corporation')
  
  return(corpName)
}

characterID <- getCharacterID('Cog Vokan')
corp.name <- getCorpName(characterID)
a <- getKillCount(characterID, '201611')

