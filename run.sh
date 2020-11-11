#!/bin/bash

run_vscode() {
	code .
}
run_project() {
	sudo docker-compose up
}

run_test() {
	sudo docker-compose run app sh -c "python manage.py wait_for_db && pytest"
}


choice_function() {

	echo "CHOOSE"
	echo "0 > just start app"
	echo "1 > start app and work vscode"
	echo "2 > test"

	read choice

	case "$choice" in 
	"0")
		run_project
	;;
		
	"1")
		run_project && run_vscode
	;;

	"2")
		run_test
	;;

	*) echo "please chose correct number"
		if [[ $# -eq 0 ]] ; then
			choice_function
		fi
	;;
	esac

}

choice_function
