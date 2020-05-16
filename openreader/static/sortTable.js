// Code adapted from w3schools.com
function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("bookTable");
    switching = true;

    // Set the sorting direction to ascending:
    dir = "asc";

    // Make a loop that will continue until no switching has been done
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;

        // Loop through all table rows (except the first, which contains table headers)
        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;

            // Get the two elements you want to compare, one from current row and one from the next
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];

            // Check if the two rows should switch place, based on the direction, asc or desc
            if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            // If a switch has been marked, make the switch and mark that a switch has been done
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;

            // Each time a switch is done, increase this count by 1:
            switchcount ++;
        } else {
            // If no switching has been done AND the direction is "asc", set the direction to "desc" and run the while loop again.
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }

    // Add symbol to html to display if it is ascending or descending order
    var header;
    // If title was clicked
    if (n == 1) {
        document.getElementById("author").textContent = "Author  ↕";		// Reset Author header if Title header was clicked
        header = document.getElementById("title");
        if (dir == "asc") {
            header.textContent = "Title  ↑";
        } else if (dir == "desc")  {
            header.textContent = "Title  ↓";
        }
    } else if (n == 2) {	// If author was clicked
        document.getElementById("title").textContent = "Title  ↕";			// Reset Title header if Author header was clicked
        header = document.getElementById("author");
        if (dir == "asc") {
            header.textContent = "Author  ↑";
        } else if (dir == "desc") {
            header.textContent = "Author  ↓";
        }
    }

}