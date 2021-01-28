# -*- coding: utf-8 -*-
from pyparsing import *
from itertools import chain
from collections import namedtuple


class DrcFileParser:
    def __init__(self, file):
        self.pathslist = []
        self.allRuleList = []
        self.densityRulesList = []
        self.densityPathsList = []
        self.search_includes(file)
        self.search_density_rules()
        self.search_density_paths()

    #Функция поиска прикрепленных к исходному файлу ссылок. В ней же проводится поиск правил по исходному и всем вложенным файлам.
    def search_includes(self, file):
        self.initfile = file
        self.drcString = self.initfile.read()
        self.initfile.close()
        self.search_drc_rules() #Поиск правил в изначально указанном файле(с которым создавался класс)
        keyinclude = "INCLUDE"
        includepath = Word(alphanums + "$/.")
        fullpath = Suppress(keyinclude + ' ') + includepath
        allpaths = OneOrMore(fullpath)
        self.pathslist.extend(list(chain.from_iterable(allpaths.searchString(self.drcString).asList())))

        for i in self.pathslist:
                if i == 'readed': continue
                bufferi = i
                print('pathlist: ', self.pathslist)
                indexOfReadedInclude = self.pathslist.index(i)
                self.pathslist[indexOfReadedInclude] = 'readed'
                try:
                    includedFile = open(bufferi, 'r')
                except IOError:
                    print("file " + str(bufferi) + " didn't exist")
                else:
                    print("all fine")
                    self.search_includes(includedFile) #Рекурсивный вызов функции с вложенным файлом как новым аргументом
    #Формирование основного списка [Имя, правило]
    def search_drc_rules(self):
        keyName = Word(printables)
        params = Word(printables + " " + 'μ' + "\n", excludeChars='{}')
        paramsWord = Suppress('{') + params + Suppress('}')
        allNotes = OneOrMore(Group(keyName + Optional(" ") + paramsWord))
        self.allRuleList.extend(list(chain.from_iterable(allNotes.searchString(self.drcString).asList())))
    #Поиск правил с маркером density внутри основного списка правил
    def search_density_rules(self):
        for rule in self.allRuleList:
            if ("density" or "DENSITY") in rule[1]:
                self.densityRulesList.append(rule)
    #Поиск ссылок на файлы в списке dens правил
    def search_density_paths(self):
        denspath = Word(printables + "./_", excludeChars='"')
        denspathfull = Suppress('"') + denspath + Suppress('"')

        for rule in enumerate(self.densityRulesList):
            self.densityPathsList.append([rule[1][0]] + list(
                chain.from_iterable(denspathfull.searchString(rule[1]).asList())))  # список [[имя, ]]

        # Удаление пустых полей
        fix = []
        for i in enumerate(self.densityPathsList):
            if len(i[1]) == 1:
                fix.append(i[0])

        for i in reversed(fix):
            self.densityPathsList.pop(i)

    # Вывод результатов парсинга.
    # 'list' или без аргумента для вывода в формате списка,
    # 'namedtuple' для именованного кортежа
    def get_parse_results(self, type = 'list'):
        rules = []
        if type == 'namedtuple':
            Rule = namedtuple('Rule', 'Name RuleText')
            for r in self.allRuleList:
                rules.append(Rule(r[0], r[1]))
        elif type == 'list':
            rules = self.allRuleList

        return rules

    def get_density_rules(self, type = 'list'):
        dens_rules = []
        if type == 'namedtuple':
            DensityRule = namedtuple('DensityRule', 'Name RuleText')
            for dr in self.densityRulesList:
                dens_rules.append(DensityRule(dr[0], dr[1]))
        elif type == 'list':
            dens_rules = self.densityRulesList

        return dens_rules

    def get_density_paths_list(self, type = 'list'):
        dens_paths = []
        if type == 'namedtuple':
            DensityPath = namedtuple('DensityPath', 'Name DensityPaths')
            for dp in self.densityPathsList:
                dp2 = dp
                dp2.pop(0)

                dens_paths.append(DensityPath(dp[0], dp2))
        elif type == 'list':
            dens_paths = self.densityPathsList
        return dens_paths


if __name__ == "__main__":
    drcFile = open('calibretest.drc', 'r')
    drcTest = DrcFileParser(drcFile)

    Presults = drcTest.get_parse_results()  # namedtuple/list
    PresultsTuple = drcTest.get_parse_results('namedtuple')
    DensityRules = drcTest.get_density_rules()
    DensityRulesTuple = drcTest.get_density_rules('namedtuple')
    DensityPaths = drcTest.get_density_paths_list()
    DensityPathsTuple = drcTest.get_density_paths_list('namedtuple')

    Otuputfile = open('outputrules.txt', 'w')
    print >> Otuputfile, len(Presults)
    print >> Otuputfile
    for element in Presults:
        print >>Otuputfile, element
        print >>Otuputfile
    Otuputfile.close()

    Otuputfile = open('outputrulestup.txt', 'w')
    print >> Otuputfile, len(PresultsTuple)
    print >> Otuputfile
    for element in PresultsTuple:
        print >> Otuputfile, element
        print >> Otuputfile
    Otuputfile.close()

    Otuputfile1 = open('outputdens.txt', 'w')
    print >> Otuputfile1, len(DensityRules)
    print >> Otuputfile1
    for element1 in DensityRules:
        print >> Otuputfile1, element1
        print >> Otuputfile1
    Otuputfile1.close()

    Otuputfile11 = open('outputdenstuple.txt', 'w')
    print >> Otuputfile11, len(DensityRulesTuple)
    print >> Otuputfile11
    for element11 in DensityRulesTuple:
        print >> Otuputfile11, element11
        print >> Otuputfile11
    Otuputfile11.close()

    Otuputfiledenspaths = open('outputdenspaths.txt', 'w')
    print >> Otuputfiledenspaths, len(DensityPaths)
    print >> Otuputfiledenspaths
    for element2 in DensityPaths:
        print >> Otuputfiledenspaths, element2
        print >> Otuputfiledenspaths
    Otuputfiledenspaths.close()

    Otuputfiledenspathstuple = open('outputdenspathstuple.txt', 'w')
    print >> Otuputfiledenspathstuple, len(DensityPathsTuple)
    print >> Otuputfiledenspathstuple
    for element22 in DensityPathsTuple:
        print >> Otuputfiledenspathstuple, element22
        print >> Otuputfiledenspathstuple
    Otuputfiledenspathstuple.close()

    #print ('parse results: ', drcTest.get_parse_results())
    drcFile.close()

