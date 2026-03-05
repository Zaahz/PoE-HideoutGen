import argparse, textwrap
def parse_args():
    parser = argparse.ArgumentParser(
        # Set the name of the program, this shows up after "usage:" if you run -h
        prog='fmg_api_test.py',
        description=textwrap.dedent('''\
                                    This script is used to test FortiManager API calls for route and policy lookups.
                                    '''),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
                            For any questions or issues, please contact Team Hugin on slack in #hugin-public.
                            ''')
    )
    
    parser.add_argument('-u', '--user', help='Username to be used for login')
    parser.add_argument('-s', '--source-ip', help='Source IP for policy lookup')
    parser.add_argument('-d', '--destination-ip', help='Destination IP for policy lookup')
    parser.add_argument('-f', '--firewall', help='Firewall to be used for route and policy lookup')
    parser.add_argument('-p', '--destination-port', type=int, help='Destination port for policy lookup')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output for debugging')
    
    
    # Check if any argument is set, and print help if not(then exit) or continue as normal if set.
    argument_set = False
    for argument in vars(parser.parse_args()):
        if vars(parser.parse_args())[argument] != None:
            argument_set = True
            break
            
    if argument_set == False:
        #parser.print_help()
        #quit()
        print("\nNo arguments provided, continuing with interactive mode...\n")
    if argument_set == True:
        return parser.parse_args()
    return False