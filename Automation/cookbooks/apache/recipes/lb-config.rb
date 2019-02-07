service 'apache2'

template '/etc/apache2/conf-available/balancer.conf' do
	source 'balancer.conf.erb'
  mode '0755'
  owner 'root'
  group 'root'
  notifies :restart, 'service[apache2]', :delayed
end

link '/etc/apache2/conf-enabled/balancer.conf' do
  to '../conf-available/balancer.conf'
  notifies :restart, 'service[apache2]', :delayed
end

%w[proxy.conf proxy.load proxy_http.load proxy_balancer.conf proxy_balancer.load slotmem_shm.load lbmethod_byrequests.load].each do |mod|
  link "/etc/apache2/mods-enabled/#{mod}" do
    to "../mods-available/#{mod}"
    notifies :restart, 'service[apache2]', :delayed
  end
end





