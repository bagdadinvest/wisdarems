$(document).ready(function() {
    let selectedCommand = null;

    // Initialize DataTables
    const dataTable = $('#commandOutputTable').DataTable({
        paging: false,  // Disable pagination (optional)
        searching: false,  // Disable searching (optional)
        ordering: false  // Disable column sorting (optional)
    });

    // Handle clicking on a predefined command
    $('.command-item').click(function() {
        // Retrieve command details from the clicked element
        selectedCommand = $(this).data('command-name');
        const commandDefinition = $(this).data('command-definition');
        const commandUsage = $(this).data('command-usage');

        // Update command details in the UI
        $('#command-name').text(selectedCommand);
        $('#command-definition').text(commandDefinition);
        $('#command-usage').text(commandUsage);

        // Enable the Run Selected Command button
        $('#runCommandButton').prop('disabled', false);
    });

    // Handle running the selected predefined command
    $('#runCommandButton').click(function() {
        if (selectedCommand) {
            dataTable.clear(); // Clear the DataTable before appending new results
            $('#terminal').empty(); // Clear the terminal as well

            const source = new EventSource(`/metrics/run-predefined-command/?command=${selectedCommand}`);

            source.onmessage = function(event) {
                // Append output to the DataTable
                const formattedOutput = `<tr><td>${event.data}</td></tr>`;
                dataTable.row.add($(formattedOutput)).draw();

                // Additionally show the output in the terminal
                $('#terminal').append(event.data + "\n");
                $('#terminal').scrollTop($('#terminal')[0].scrollHeight);
            };

            source.onerror = function(event) {
                source.close();
            };
        }
    });

    // Handle running a custom command
    $('#runCustomCommandButton').click(function() {
        const customCommand = $('#customCommandInput').val().trim();
        if (customCommand) {
            dataTable.clear(); // Clear previous output from the DataTable
            $('#terminal').empty(); // Clear the terminal output

            const source = new EventSource(`/metrics/run-custom-command/?custom_command=${encodeURIComponent(customCommand)}`);

            source.onmessage = function(event) {
                // Append output to the DataTable
                const formattedOutput = `<tr><td>${event.data}</td></tr>`;
                dataTable.row.add($(formattedOutput)).draw();

                // Also append output to the terminal
                $('#terminal').append(event.data + "\n");
                $('#terminal').scrollTop($('#terminal')[0].scrollHeight);
            };

            source.onerror = function(event) {
                source.close();
            };
        } else {
            alert(translations.enterCommand);  // Using the passed translations
        }
    });
});
