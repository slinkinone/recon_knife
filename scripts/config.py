#!/usr/bin/env python

general = {
	"tools_folder_path": "~/tools",
	"all_domain_filename": "all_domain.txt",
	"domain_recon_path": "",
}

input_data = {
	"domain": "",
	"excluded_domains": "",
}

sublist3r = {
    "run_path": general["tools_folder_path"] + "/Sublist3r/sublist3r.py",
    "out_filename": "sublist3r.txt",
    "thread_count": 10,
}

massdns = {
	"run_path": general["tools_folder_path"] + "/massdns/bin/massdns",
	"scripts_path": general["tools_folder_path"] + "/massdns/scripts",
	
	"crtsh_script_name": "ct.py",
	"subbrute_script_name": "subbrute.py",

	"resolvers_path": general["tools_folder_path"] + "/massdns/lists/resolvers.txt",

	"word_list": general["tools_folder_path"] + "/SecLists/Discovery/DNS/clean-jhaddix-dns.txt",

	"crtsh_out_file": "massdns_crtsh.txt",
	"sublist3r_out_file": "massdns_sublist3r.txt",
	"certspotter_out_file": "massdns_certspotter.txt",
	"subbrute_out_file": "massdns_subbrute.txt",

	# TODO: clarify what is this IP
	"some_ip": "142.54.173.92",
}

certspotter = {
	# TODO: https://api.certspotter.com/v1/issuances?domain=hackerone.com&expand=dns_names&expand=issuer&expand=cert
	"format_url": "https://certspotter.com/api/v0/certs?domain={}",
	"out_filename": "certspotter.txt",
}

hostalive = {
    "out_filename": "urllist.txt",
}

aqua = {
    "out_folder_name": "aqua_out",
    "chromium_path": "/usr/bin/chromium",
    "countThreads": 5,
}

waybackurls = {
	"out_folder_name": "wayback_data",
	"out_filename": "waybackurls.txt",
	"params_filename": "paramlist.txt",
	"jsurls_filename": "jsurls.txt",
	"phpurls_filename": "phpurls.txt",
	"aspxurls_filename": "aspxurls.txt",
	"jspurls_filename": "jspurls.txt",
}

dirsearcher = {
	"run_path": general["tools_folder_path"] + "dirsearch/dirsearch.py",
	"subdomain_threads": 10,
	"dirsearch_threads": 10,
	"dirsearch_wordlist": general["tools_folder_path"] + "db/dicc.txt",
}

nmap = {
	"ports": [2075, 2076, 6443, 3868, 3366, 8443, 8080, 9443, 9091,
				3000, 8000, 5900, 8081, 6000, 10000, 8181, 3306,
				5000, 4000, 8888, 5432, 15672, 9999, 161, 4044,
				7077, 4040, 9000, 8089, 443, 7447, 7080, 8880,
				8983, 5673, 7443, 19000, 19080],
}