"""
Network config updater for a DoseNet silicon radiation detector station.

This script securely copies the Raspberry Pi network configuration file from
the DoseNet servers to a detector at a school of interest and updates the
network ID on the network configuration file for the Rasberry Pi, as well as
handles netmasks, gateways, and DNS server names to setup a static IP if
necessary. (A dynamic IP is set by default.)
"""

# Import the relevant modules and functions from the appropriate libraries.
import fileinput
import os
import sys


'''
Part 1: Define a function to update the interfaces file by replacing the
        line containing an indicated phrase with a new line.
'''


def interfaces_update(rep_phrase, new_line):
    """Main function to update the network interfaces file."""
    '''
    Store the normal standard input and output. This allows us to restore
    them later to access the standard input and output for other uses
    outside of this function, such as raw_input and print statements.
    '''
    temp_in = sys.stdin
    temp_out = sys.stdout

    # Open the interfaces file for reading and open up a temporary file for
    # writing using the standard input and output functions.
    sys.stdin = open('/etc/network/interfaces', 'r')
    sys.stdout = open('~interfaces_temp', 'w')

    '''
    Loop through each line of the interfaces file to find the phrase of
    interest and replace it with the new line.
    '''

    for line in fileinput.input('/etc/network/interfaces'):

        # Search and find the phrase of interest to indicate the place in the
        # code to replace the original line with the new line.
        if rep_phrase in line:

            # Create a handle for a new line with the updated phrase to input
            # into the interfaces file.
            line = new_line

        # Write the new line with the updated phrase in the temporary
        # interfaces file. Also copy all other lines.
        sys.stdout.write(line)

    # Move the updated interfaces file to replace the old interfaces file
    # using root access.
    os.system('sudo mv ~interfaces_temp /etc/network/interfaces')

    # Close the interfaces files for reading and writing
    sys.stdout.close()

    # Return the original standard input and output to normal.
    sys.stdin = temp_in
    sys.stdout = temp_out

'''
Part 2: Define a function to restore the backup of the interfaces file.
'''


def backup_restore():
    """Function to restore the interfaces file with the backup."""
    '''
    Restore the backup interfaces file using the cp linux command
    with root access.
    '''
    os.system('sudo cp /etc/network/interfaces_backup ' +
              '/etc/network/interfaces')

    # Alert the user that the backup interfaces file has been restored
    # and to re-run the script if they want to re-setup the network
    # configuration.
    print('\nThe network interfaces file has been restored from the ' +
          'backup and changes have been reverted. Run this Python ' +
          'script again to setup the network configuration again.')

'''
Part 3: Define a function to restore the dynamic IP configuration if a faulty
        static IP configuration has been set (i.e., one without one of the
        following: netmask, gateway, DNS server names).

        Namely, the static IP, netmask, and gateway calls are commented out
        and the dynamic IP calls are uncommented out. The DNS server names are
        unaffected as they
'''


def dynamic_restore(static, netmask, gateway):
    """Function to restore the dynamic IP configuration."""
    '''
    Update the interfaces file with the dynamic IP by uncommenting out the
    dynamic IP call and commenting out the static IP calls.
    '''
    interfaces_update('# replace for dynamic IP configuration' + '\n' +
                      '# iface eth0 inet dhcp', 'iface eth0 inet dhcp\n')
    interfaces_update('# auto eth0', 'auto eth0' + '\n')
    interfaces_update('iface eth0 inet static', '# iface eth0 inet static' +
                      '\n')

    # Update the interfaces file with the static IP by uncommenting out
    # the static IP call.
    interfaces_update('  address {}'.format(static), '#   address\n')

    # Remove the netmask and gateway identifiers from the interfaces
    # file by commenting them out.
    interfaces_update('  netmask {}'.format(netmask), '#   ' +
                      'netmask\n')

    interfaces_update('  gateway {}'.format(gateway), '#   ' +
                      'gateway\n')

'''
Part 4: Securely copy the network configuration (csv) file from the Dosenet
        servers to the Raspberry Pi if the user so wishes.
'''

# Ask the user if they would like to copy a new network configuration file
# from the LBNL servers.
csv_copy = raw_input('\nWould you like to copy a new network configuration ' +
                     '(csv) file from the LBNL servers (y/n)?: ')

'''
If there is no valid response, let the user know and repeat the prompt until a
valid response is provided.

If the response is a yes, ask for the network configuration (csv) file name
and securely copy it from the LBNL servers.

If the response is a no, simply let the user know the script will henceforth
assume that there is a csv file, and continue with the script.
'''

while csv_copy.lower() not in ('y', 'n'):

    # Let the user know a valid response is required for the question.
    print('Please provide a valid "y" or "n" response.')

    # Ask the user if they would like to copy a new network configuration file
    # from the LBNL servers.
    csv_copy = raw_input('\nWould you like to copy a new network ' +
                         'configuration (csv) file from the LBNL servers ' +
                         '(y/n)?: ')

if csv_copy.lower() == 'y':

    # Ask the user for the csv file name and output the raw input string as a
    # variable.
    name = raw_input('\nWhat is the network configuration (csv) file name?: ')

    # Define the paths to the source and target csv files as arguments for the
    # scp linux command to be executed through the os.system function. Note: A
    # password to the DoseNet servers in LBNL will be requested at this point
    # in the script.
    sourcePath = 'dosenet@dosenet.dhcp.lbl.gov:~/config-files/' + name
    targetPath = '/home/pi/config/config.csv'

    # Execute the scp linux command line to securely copy the file over the
    # Internet.
    os.system('scp {} {}'.format(sourcePath, targetPath))

elif csv_copy.lower() == 'n':

    raw_input('\nNote: There must be a network configuration file to ' +
              'properly configure the network options. Please double-check ' +
              'before continuing. Exit and rerun the script to get a ' +
              'prompt to copy the network configuration file. Press any ' +
              'key to continue. ')

'''
Part 5: Update the dosimeter ID on the network configuration file on the
        Raspberry Pi once it has been copied securely over the Internet.
'''

# Backup the interfaces file through the cp linux command to make a backup copy
# of the interfaces file before any editing is done.
os.system('sudo cp /etc/network/interfaces /etc/network/interfaces_backup')

# Alert the user that a backup file has been made and changes can be kept or
# reverted later.
print('\nA backup of the network interfaces file has been made. If you ' +
      'make an error during the rest of the setup, a prompt at the end ' +
      'will ask if you would like to keep the changes made and restore the ' +
      'backup to the interfaces file.')

# Ask for the station ID and output the raw input string as a variable.
id = raw_input('\nWhat is the station ID?: ')

# Update the station ID using the update function.
interfaces_update('wireless-essid RPiAdHocNetwork', '  wireless-essid ' +
                  'RPiAdHocNetwork{}'.format(id) + '\n')

# Ask the user if they would like to use a static IP.
setup_static_ip = raw_input('\nDo you want to set a static IP (y/n)?: ')

'''
If there is no valid response, let the user know and repeat the prompt until a
valid response is provided.

If the response is a no, ask additionally if the the user would like to keep
the changes done to the network interfaces file.

If the response is a yes, update the interfaces file to include the static IP
and the relevant functionality.
'''

while setup_static_ip.lower() not in ('y', 'n'):

    # Let the user know a valid response is required for the question.
    print('Please provide a valid "y" or "n" response.')

    # Re-ask the user if they would like to use a static IP.
    setup_static_ip = raw_input('\nDo you want to set a static IP (y/n)?: ')

if setup_static_ip.lower() == 'n':

    # Ask the user if they would like to keep the changes to the network
    # interfaces file.
    keep_changes = raw_input('\nWould you like to keep these changes ' +
                             '(y/n)?: ')

    '''
    If there is no valid response, let the user know and repeat the prompt
    until a valid response is provided.

    If the response is a yes, exit the script and tell the user the network
    interfaces file has been updated.

    If the response is a no (or anything else), restore the backup to the
    network interfaces file.
    '''

    while keep_changes.lower() not in ('y', 'n'):

        # Let the user know a valid response is required for the question.
        print('Please provide a valid "y" or "n" response.')

        # Ask the user if they would like to keep the changes to the network
        # interfaces file.
        keep_changes = raw_input('\nWould you like to keep these changes ' +
                                 '(y/n)?: ')

    if keep_changes.lower() == 'y':

        print('\nA dynamic IP has been set. Your Pi-hat sensor module now ' +
              'has updated network functionality and the appropriate ' +
              'network interfaces file has been copied over from the ' +
              'DoseNet servers.')

    elif keep_changes.lower() == 'n':

        # Restore the backup for the interfaces file.
        backup_restore()

    sys.exit()

elif setup_static_ip.lower() == 'y':

    # Ask for the static IP.
    ip_static = raw_input('\nWhat is your static IP?: ')

    # Update the interfaces file with the static IP by commenting out the
    # dynamic IP call and uncommenting out the static IP calls.
    interfaces_update('iface eth0 inet dhcp', '# replace for dynamic IP ' +
                      'configuration' + '\n' + '# iface eth0 inet dhcp' +
                      '\n')
    interfaces_update('# auto eth0', 'auto eth0' + '\n')
    interfaces_update('# iface eth0 inet static', 'iface eth0 inet static' +
                      '\n')
    interfaces_update('#   address', '  address {}'.format(ip_static) + '\n')

    # Ask the user if they have a netmask.
    setup_netmask = raw_input('\nDo you have a netmask (y/n)?: ')

    '''
    If there is no valid response, let the user know and repeat the prompt
    until a valid response is provided.

    If the response is a no, ask additionally if the the user would like to
    keep the changes done to the network interfaces file.

    If the response is a yes, update the interfaces file to include the netmask
    identifier and the relevant functionality.
    '''

    while setup_netmask.lower() not in ('y', 'n'):

        # Let the user know a valid response is required for the question.
        print('Please provide a valid "y" or "n" response.')

        # Ask the user if they have a netmask.
        setup_netmask = raw_input('\nDo you have a netmask (y/n)?: ')

    if setup_netmask.lower() == 'n':

        # Ask the user if they would like to keep the changes to the network
        # interfaces file.
        keep_changes = raw_input('\nWould you like to keep these changes ' +
                                 '(y/n)?: ')

        '''
        If there is no valid response, let the user know and repeat the prompt
        until a valid response is provided.

        If the response is a yes, exit the script and tell the user the network
        interfaces file has been updated.

        If the response is a no (or anything else), restore the backup to the
        network interfaces file.
        '''

        while keep_changes.lower() not in ('y', 'n'):

            # Let the user know a valid response is required for the question.
            print('Please provide a valid "y" or "n" response.')

            # Ask the user if they would like to keep the changes to the
            # network interfaces file.
            keep_changes = raw_input('\nWould you like to keep these ' +
                                     'changes (y/n)?: ')

        if keep_changes.lower() == 'y':

            # Restore the dynamic IP configuration.
            dynamic_restore(ip_static, 'dummy', 'dummy')

            print('\nA static IP has not been set (requires a netmask, ' +
                  'a gateway, and DNS server names) and a dynamic IP will ' +
                  'remain. Your Pi-hat sensor module now has updated ' +
                  'network functionality and the appropriate network ' +
                  'interfaces file has been copied over from the DoseNet ' +
                  'servers.')

        elif setup_netmask.lower() == 'n':

            # Restore the backup for the interfaces file.
            backup_restore()

        sys.exit()

    elif setup_netmask.lower() == 'y':

        # Ask for the netmask identifier.
        netmask_id = raw_input('\nWhat is your netmask identifier?: ')

        # Update the interfaces file with the netmask identifier by
        # uncommenting out the netmask call.
        interfaces_update('#   netmask', '  netmask {}'.format(netmask_id) +
                          '\n')

    # Ask the user if they have a gateway.
    setup_gateway = raw_input('\nDo you have a gateway (y/n)?: ')

    '''
    If there is no valid response, let the user know and repeat the prompt
    until a valid response is provided.

    If the response is a no, ask additionally if the the user would like to
    keep the changes done to the network interfaces file.

    If the response is a yes, update the interfaces file to include the gateway
    identifier and the relevant functionality.
    '''

    while setup_gateway.lower() not in ('y', 'n'):

        # Let the user know a valid response is required for the question.
        print('Please provide a valid "y" or "n" response.')

        # Ask the user if they have a gateway.
        setup_gateway = raw_input('\nDo you have a gateway (y/n)?: ')

    if setup_gateway.lower() == 'n':

        # Ask the user if they would like to keep the changes to the network
        # interfaces file.
        keep_changes = raw_input('\nWould you like to keep these changes ' +
                                 '(y/n)?: ')

        '''
        If there is no valid response, let the user know and repeat the prompt
        until a valid response is provided.

        If the response is a yes, exit the script and tell the user the network
        interfaces file has been updated.

        If the response is a no (or anything else), restore the backup to the
        network interfaces file.
        '''

        while keep_changes.lower() not in ('y', 'n'):

            # Let the user know a valid response is required for the question.
            print('Please provide a valid "y" or "n" response.')

            # Ask the user if they would like to keep the changes to the
            # network interfaces file.
            keep_changes = raw_input('\nWould you like to keep these ' +
                                     'changes (y/n)?: ')

        if keep_changes.lower() == 'y':

            # Restore the dynamic IP configuration.
            dynamic_restore(ip_static, netmask_id, 'dummy')

            print('\nA static IP has not been set (requires a netmask, ' +
                  'a gateway, and DNS server names) and a dynamic IP will ' +
                  'remain. Your Pi-hat sensor module now has updated ' +
                  'network functionality and the appropriate network ' +
                  'interfaces file has been copied over from the DoseNet ' +
                  'servers.')

        elif keep_changes.lower() == 'n':

            # Restore the backup for the interfaces file.
            backup_restore()

        sys.exit()

    elif setup_gateway.lower() == 'y':

        # Ask for the gateway identifier.
        gateway_id = raw_input('\nWhat is your gateway identifier?: ')

        # Update the interfaces file with the gateway identifier by
        # uncommenting out the gateway call.
        interfaces_update('#   gateway', '  gateway {}'.format(gateway_id) +
                          '\n')

    # Ask the user if they have DNS servers connected.
    setup_dns_server = raw_input('\nDo you have DNS servers connected ' +
                                 '(y/n)?: ')

    '''
    If there is no valid response, let the user know and repeat the prompt
    until a valid response is provided.

    If the response is a no, ask additionally if the the user would like to
    keep the changes done to the network interfaces file.

    If the response is a yes, update the interfaces file to include the DNS
    server names and the relevant functionality.
    '''
    while setup_dns_server.lower() not in ('y', 'n'):

        # Let the user know a valid response is required for the question.
        print('Please provide a valid "y" or "n" response.')

        # Ask the user if they have DNS servers connected.
        setup_dns_server = raw_input('\nDo you have DNS servers connected ' +
                                     '(y/n)?: ')

    if setup_dns_server.lower() == 'n':

        # Ask the user if they would like to keep the changes to the network
        # interfaces file.
        keep_changes = raw_input('\nWould you like to keep these changes ' +
                                 '(y/n)?: ')

        '''
        If there is no valid response, let the user know and repeat the prompt
        until a valid response is provided.

        If the response is a yes, exit the script and tell the user the network
        interfaces file has been updated.

        If the response is a no (or anything else), restore the backup to the
        network interfaces file.
        '''

        while keep_changes.lower() not in ('y', 'n'):

            # Let the user know a valid response is required for the question.
            print('Please provide a valid "y" or "n" response.')

            # Ask the user if they would like to keep the changes to the
            # network interfaces file.
            keep_changes = raw_input('\nWould you like to keep these ' +
                                     'changes (y/n)?: ')

        if keep_changes.lower() == 'y':

            # Restore the dynamic IP configuration.
            dynamic_restore(ip_static, netmask_id, gateway_id)

            print('\nA static IP has not been set (requires a netmask, ' +
                  'a gateway, and DNS server names) and a dynamic IP will ' +
                  'remain. Your Pi-hat sensor module now has updated ' +
                  'network functionality and the appropriate network ' +
                  'interfaces file has been copied over from the DoseNet ' +
                  'servers.')

        elif keep_changes.lower() == 'n':

            # Restore the backup for the interfaces file.
            backup_restore()

        sys.exit()

    elif setup_dns_server.lower() == 'y':

        # Ask for the DNS server names.
        dns_server_1 = raw_input('\nWhat is the IP of the first DNS ' +
                                 'server?: ')
        dns_server_2 = raw_input('\nWhat is the IP of the second DNS ' +
                                 'server?: ')

        # Update the interfaces file with the DNS server names by uncommenting
        # out the DNS server names call.
        interfaces_update("#   dns-nameservers", "  dns-nameservers " +
                          "{} {}".format(dns_server_1, dns_server_2) + '\n')

'''
Part 6: Perform a final check on whether the user wants to keep the changes
        to the interfaces file and output the results of the configuration of
        a static IP if the script has not been exited at this point.
'''

# Ask the user if they would like to keep the changes to the network
# interfaces file.
keep_changes = raw_input('\nWould you like to keep these changes (y/n)?: ')

'''
If there is no valid response, let the user know and repeat the prompt
until a valid response is provided.

If the response is a yes, exit the script and tell the user the network
interfaces file has been updated.

If the response is a no (or anything else), restore the backup to the
network interfaces file.
'''

while keep_changes.lower() not in ('y', 'n'):

    # Let the user know a valid response is required for the question.
    print('Please provide a valid "y" or "n" response.')

    # Re-ask the user if they would like to keep the changes to the network
    # interfaces file.
    keep_changes = raw_input('\nWould you like to keep these changes (y/n)?: ')

if keep_changes.lower() == 'y':

    print('\nA static IP has been set with your indicated netmask, gateway, ' +
          'and DNS server name identifiers. Your Pi-hat sensor module now ' +
          'has updated network functionality and the appropriate network ' +
          'interfaces file has been copied over from the DoseNet servers.')

elif keep_changes.lower() == 'n':

    # Restore the backup for the interfaces file.
    backup_restore()
