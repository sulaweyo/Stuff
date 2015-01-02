#!/usr/bin/perl -w
#
# This CGI will collect the cluster information and display it.
#
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use Net::Domain qw(hostname hostfqdn hostdomain);
use warnings;
use strict;

# Variables
my $cluster_name = "lnz-srv-arch-cl01";
my %nodes = ("lnz-srv-arch-cl01-1v", "lnz-srv-arch-cl01-2v");
my %colors = (  "red",   "#ff0000",
                "green", "#00ff00",
                "blue",  "#0000ff",
                "black", "#000000",
                "gray",  "#F8F8F8",
                "white", "#ffffff" );
my $host = hostname;
my $domain = hostdomain;
my $fqdn = hostfqdn;

# Helper functions
# Read the load average.
sub loadavg {
        # Read the values from /proc/loadavg and put them in an array.
        open FILE, "< /proc/loadavg" or die return ("Cannot open /proc/loadavg: $!");
                my ($avg1, $avg5, $avg15, undef, undef) = split / /, <FILE>;
                my @loadavg = ($avg1, $avg5, $avg15);
        close FILE;
        return (@loadavg);
}

# Read the number of CPU's.
sub cpu_cnt {
        # Read the data from /proc/cpuinfo and count the lines that start with processor blablabla :-)
        open FILE, "< /proc/cpuinfo" or die return ("Cannot open /proc/cpuinfo: $!");                                                
                my $cpus = scalar grep(/^processor\s+:/,<FILE>);                                                                     
        close FILE;                                                                                                                  
        return ($cpus);                                                                                                              
}                                                                                                                                    
                                                                                                                                     
# Read the uptime.                                                                                                                   
sub uptime {                                                                                                                         
        # Read the uptime in seconds from /proc/uptime, skip the idle time...                                                        
        open FILE, "< /proc/uptime" or die return ("Cannot open /proc/uptime: $!");                                                  
                my ($uptime, undef) = split / /, <FILE>;                                                                             
        close FILE;                                                                                                                  
        $uptime = sprintf("%.2f", $uptime / 86400); #return days                                                                     
        return ($uptime);                                                                                                            
}                                                                                                                                    
                                                                                                                                     
# Read the meminfo                                                                                                                   
sub meminfo {                                                                                                                        
        open FILE, "< /proc/meminfo" or die return ("Cannot open /proc/meminfo: $!");                                                
                my @meminfo = grep(/^Mem.*/, <FILE>);                                                                                
        close FILE;                                                                                                                  
        return (@meminfo);                                                                                                           
}                                                                                                                                    
                                                                                                                                     
# Get network interfaces                                                                                                             
sub interfaces {                                                                                                                     
        my $interface;                                                                                                               
        my %IPs;                                                                                                                     
        foreach ( qx{ (LC_ALL=C /sbin/ifconfig -a 2>&1) } ) {                                                                        
                $interface = $1 if /^(\S+?):?\s/;                                                                                    
                next unless defined $interface;                                                                                      
                $IPs{$interface}->{STATE}=uc($1) if /\b(up|down)\b/i;                                                                
                $IPs{$interface}->{IP}=$1 if /inet\D+(\d+\.\d+\.\d+\.\d+)/i;                                                         
        }                                                                                                                            
        return (%IPs);                                                                                                               
}                                                                                                                                    
                                                                                                                                     
# Print out functions                                                                                                                
# Get system details into hash                                                                                                       
sub gather_host_details {
        my %hd_hash = ();
        $hd_hash{'uptime'} = &uptime();
        $hd_hash{'cpu_cnt'} = &cpu_cnt();
        my @load = &loadavg();
        $hd_hash{'load1'} = $load[0];
        $hd_hash{'load5'} = $load[1];
        $hd_hash{'load15'} = $load[2];
        my @mem = &meminfo();
        $hd_hash{'memT'} = @mem[0];
        $hd_hash{'memF'} = @mem[1];
        $hd_hash{'memA'} = @mem[2];
        return (%hd_hash);
}

# Print the header
sub print_site_header {
        if (exists($nodes{$host})) {
                print h2("<center>Welcome to the Cluster <font color=\"$colors{green}\">$cluster_name</font></center>");
                print h4("<center>You are currently at host <font color=\"$colors{blue}\">$fqdn</font></center>");
        } else {
                print h2("<center>Welcome to the node <font color=\"$colors{blue}\">$fqdn</font></center>");
                print h4("<center><font color=\"$colors{red}\">This host is not a cluster member of $cluster_name!</font></center>");
        }
}

# Print all the host detail
sub print_host_details {
        my %hd = &gather_host_details();
        print qq(<div id='host_detail'>);
        print qq(<div id='host_detail' class='header'>Host details</div>);
        print qq(<div id='entry'>Uptime: $hd{uptime} days</div>);
        print qq(<div id='entry'>Load average: $hd{load1}, $hd{load5}, $hd{load15}</div>);
        print qq(<div id='host_detail' class='header'>System information</div>);
        print qq(<div id='entry'>CPU count: $hd{cpu_cnt}</div>);
        print qq(<div id='entry'>$hd{memT}</div>);
        print qq(<div id='entry'>$hd{memF}</div>);
        print qq(<div id='entry'>$hd{memA}</div>);
        print qq(<div id='host_detail' class='header'>Interface IPs</div>);
        my %IPs = &interfaces();
        my $key;
        foreach $key (keys %IPs){ 
                if ($IPs{$key}{STATE} == 'UP') {
                        print qq(<div id='entry'>Interface => $key: $IPs{$key}{IP}</div>);
                } else {
                        print qq(div id='entry'>Interface => $key: DOWN</div>);
                }
        }
        print qq(</div>);
}

# Set the CSS definitions
sub define_css {
        print qq(<style>);
        print qq(#host_detail { margin-left : 15px; });
        print qq(#entry { margin-left : 25px; });
        print qq(.header { font-weight : bold; });
        print qq(</style>);
}

# print it out
print header;
print start_html("Cluster Info");
&define_css();
&print_site_header();
&print_host_details();
print end_html;

