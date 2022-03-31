db::setAttr geometry -of [gi::getWindows 0] -value 600x300+5+494
dm::showLibraryManager
db::setAttr geometry -of [gi::getWindows 1] -value 653x600+50+75
gi::setItemSelection {libs} -index {snpsDefTechLib} -in [gi::getWindows 1]
db::showManageTechnology
db::setAttr geometry -of [gi::getWindows 2] -value 450x400+5+49
gi::executeAction dbTechnologyFileExport -in [gi::getWindows 2]
gi::setActiveDialog [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 2]]
db::setAttr geometry -of [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 2]] -value 505x400+5+73
gi::setField {fileName} -value {snpsDef.tf} -in [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 2]]
gi::pressButton {ok} -in [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 2]]
gi::executeAction giCloseWindow -in [gi::getWindows 2]
gi::setActiveWindow 1
gi::setActiveWindow 1 -raise true
db::showManageTechnology
db::setAttr geometry -of [gi::getWindows 3] -value 450x400+5+49
db::setAttr geometry -of [gi::getWindows 3] -value 450x400+149+143
gi::executeAction dbTechnologyFileExport -in [gi::getWindows 3]
gi::setActiveDialog [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 3]]
db::setAttr geometry -of [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 3]] -value 505x400+149+192
gi::closeWindows [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 3]]
gi::executeAction dbTechnologyFileImport -in [gi::getWindows 3]
gi::setActiveDialog [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 3]]
db::setAttr geometry -of [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 3]] -value 478x400+135+167
gi::pressButton {fileNameBrowse} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 3]]
gi::setField {overwriteMode} -value {true} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 3]]
gi::pressButton {ok} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 3]]
gi::setActiveWindow 0
gi::setActiveWindow 0 -raise true
gi::setActiveDialog [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 3]]
gi::pressButton {cancel} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 3]]
gi::setActiveWindow 3
gi::setActiveWindow 3 -raise true
gi::executeAction giCloseWindow -in [gi::getWindows 3]
gi::setActiveWindow 0
gi::setActiveWindow 0 -raise true
gi::setActiveWindow 1
gi::setActiveWindow 1 -raise true
gi::setItemSelection {libs} -index {sample} -in [gi::getWindows 1]
gi::setItemSelection {libs} -index {snpsDefTechLib} -in [gi::getWindows 1]
db::showManageTechnology
db::setAttr geometry -of [gi::getWindows 4] -value 450x400+5+49
gi::executeAction dbTechnologyFileImport -in [gi::getWindows 4]
gi::setActiveDialog [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]]
db::setAttr geometry -of [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]] -value 478x400+5+49
gi::setField {replaceMode} -value {true} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]]
gi::pressButton {apply} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]]
gi::setActiveWindow 0
gi::setActiveWindow 0 -raise true
gi::pressButton {ok} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]]
gi::setActiveDialog [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]]
gi::pressButton {apply} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]]
gi::setActiveWindow 0
gi::setActiveWindow 0 -raise true
gi::setActiveDialog [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]]
gi::setField {overwriteMode} -value {true} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]]
gi::pressButton {ok} -in [gi::getDialogs {dbImportTechnology} -parent [gi::getWindows 4]]
gi::executeAction dbTechnologyFileExport -in [gi::getWindows 4]
gi::setActiveDialog [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 4]]
db::setAttr geometry -of [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 4]] -value 505x400+5+73
gi::setField {fileName} -value {s.tf} -in [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 4]]
gi::pressButton {ok} -in [gi::getDialogs {dbExportTechnology} -parent [gi::getWindows 4]]
gi::executeAction giCloseWindow -in [gi::getWindows 4]
gi::setActiveWindow 1
gi::setActiveWindow 1 -raise true
gi::executeAction giCloseWindow -in [gi::getWindows 1]
gi::setActiveWindow 0
gi::setActiveWindow 0 -raise true
gi::executeAction giCloseWindow -in [gi::getWindows 0]
