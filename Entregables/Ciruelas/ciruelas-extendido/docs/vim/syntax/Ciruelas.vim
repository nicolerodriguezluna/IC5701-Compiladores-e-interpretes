" Quit when a syntax file was already loaded.
"if exists('b:current_syntax') 
"  finish
"endif

syntax match Comment    /Bomba:.*/

syntax match Boolean /True/
syntax match Boolean /False/

syntax match Conditional /diay siii/
syntax match Conditional /sino ni modo/

syntax match Repeat /upee/
 
syntax match Keyword /mae/
syntax match Keyword /sarpe/
syntax match Keyword /jefe/
syntax match Keyword /jefa/
syntax match Keyword /metale/

syntax match Operator /echele/
syntax match Operator /quitele/
syntax match Operator /chuncherequee/
syntax match Operator /desmadeje/
syntax match Operator /divorcio/
syntax match Operator /casorio/
syntax match Operator /cañazo/
syntax match Operator /poquitico/
syntax match Operator /misma vara/
syntax match Operator /otra vara/
syntax match Operator /menos o igualitico/
syntax match Operator /mas o igualitico/

syntax region Texto start=/\~/ end=/\~/  oneline

syntax match  Number /-?[0-9]+/
syntax match  Float /-?[0-9]+\.[0-9]+/

syntax match Function /hacer_menjunje/
syntax match Function /viene bolita/
syntax match Function /trome/
syntax match Function /sueltele/
syntax match Function /echandi_jiménez/
 
syntax match Exception /safis/

highlight Function guifg=green
highlight Operator guifg=lightgreen
highlight Keyword guifg=lightblue
highlight Exception guifg=red
highlight Texto guifg=darkyellow




"let b:current_syntax = 'Ciruelas'
