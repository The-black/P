service 'apache2'

template '/var/www/html/index.html' do
  source 'index.html.erb'
  mode '0755'
  owner 'root'
  group 'root'
  notifies :restart, 'service[apache2]', :delayed
end

cookbook_file '/etc/apache2/conf-available/fixed-response.conf' do
  source 'fixed-response.conf'
  mode '0755'
  owner 'root'
  group 'root'
  notifies :restart, 'service[apache2]', :delayed
end

link '/etc/apache2/conf-enabled/fixed-response.conf' do
  to '../conf-available/fixed-response.conf'
  notifies :restart, 'service[apache2]', :delayed
end
