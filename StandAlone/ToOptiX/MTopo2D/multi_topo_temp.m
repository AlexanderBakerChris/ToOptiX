# Basis Source Code A 99 LINE TOPOLOGY OPTIMIZATION CODE BY OLE SIGMUND, OCTOBER 1999 
# Appended Sourc Code: Denk, Martin, 2015
#					   Accronym: DMST
#                      Supported By: APworks GmbH 
#					   University of applied science in munic



function multi_topo(numberElemX,numberElemY,volumenRatio,penaltyExponent,minFilterRadius, ...
                    adaptChangeIteration, adapVolFrac, NumberOfAdapChanges, weightFactorStruc,...
                    ThermalIsActive, ...
                    StructIsActive, SensitivIsActive, AdaptionIsActive, StartStrucAdap, ...
                    WeightAdapIsActive, IterativeAdapIsActive);

	#----
	# Userparameter which are needed
	#----
	# Parameter for standard topologie optimization   
    # Controplarameter IA = is active
	changePerIteration = 0.2;
	iteration = 0;
	maxIterations = 300;
    OnlyThermalIA = false
    OnlyStrucIA = false
    WeightDensIA = false
    WeightSensIA = false

    AdapStrucStartIA = false
    AdapThermStartIA = false
    ItAdapStrucStartIA = false
    ItAdapThermStartIA = false

    AdapWeighSensStrucStartIA = false
    AdapWeighDensStrucStartIA = false
    AdapWeighSensThermStartIA = false
    AdapWeighDensThermStartIA = false
    if ThermalIsActive == true && StructIsActive == false
        fprintf('Thermal Optimization is selected \n');
        OnlyThermalIA = true
    elseif ThermalIsActive == false && StructIsActive == true
        fprintf('Structural Optimization is selected \n');
         OnlyStrucIA = true
    # Only weight factors
    elseif ThermalIsActive == true && StructIsActive == true && SensitivIsActive == false && AdaptionIsActive == false
        fprintf('Weight optimization is selected (Densitys)\n');
        WeightDensIA = true
    elseif ThermalIsActive == true && StructIsActive == true && SensitivIsActive == true && AdaptionIsActive == false
        fprintf('Weight optimization is selected (Sensitives)\n');
        WeightSensIA = true
    # Adaption part pending
    elseif ThermalIsActive == true && StructIsActive == true  && AdaptionIsActive == true && StartStrucAdap == true && WeightAdapIsActive == false && IterativeAdapIsActive == true
        fprintf('Iterative Adaption with Struc start is selected\n');
        ItAdapStrucStartIA = true
    elseif ThermalIsActive == true && StructIsActive == true  && AdaptionIsActive == true && StartStrucAdap == false && WeightAdapIsActive == false && IterativeAdapIsActive == true
        fprintf('Iterative Adaption with thermal start is selected\n');
        ItAdapThermStartIA = true
    # Adaption not pending
    elseif ThermalIsActive == true && StructIsActive == true  && AdaptionIsActive == true && StartStrucAdap == true && WeightAdapIsActive == false && IterativeAdapIsActive == false
        fprintf('Adaption with Struc start is selected\n');
        AdapStrucStartIA = true
    elseif ThermalIsActive == true && StructIsActive == true  && AdaptionIsActive == true && StartStrucAdap == false && WeightAdapIsActive == false && IterativeAdapIsActive == false
        fprintf('Adaption with thermal start is selected\n');
        AdapThermStartIA = true
    # Weight Adaption struc start
    elseif ThermalIsActive == true && StructIsActive == true && SensitivIsActive == true && AdaptionIsActive == true && StartStrucAdap == true && WeightAdapIsActive == true
        fprintf('Weighted (Sensitives) Adaption with structural start is selected\n');
        AdapWeighSensStrucStartIA = true
    elseif ThermalIsActive == true && StructIsActive == true && SensitivIsActive == false && AdaptionIsActive == true && StartStrucAdap == true && WeightAdapIsActive == true
        fprintf('Weighted (Density) Adaption with structural start is selected\n');
        AdapWeighDensStrucStartIA = true
    # Weight adaption therm start
    elseif ThermalIsActive == true && StructIsActive == true && SensitivIsActive == true && AdaptionIsActive == true && StartStrucAdap == false && WeightAdapIsActive == true
        fprintf('Weighted (Sensitives) Adaption with thermal start is selected\n');
        AdapWeighSensThermStartIA = true
    elseif ThermalIsActive == true && StructIsActive == true && SensitivIsActive == false && AdaptionIsActive == true && StartStrucAdap == false && WeightAdapIsActive == true
        fprintf('Weighted (Density) Adaption with thermal is selected\n');
        AdapWeighDensThermStartIA = true
    else
        fprintf('No selection\n');
    end
    adapCounter = 1
    changePhysType = false
    addOldSolu = false
	x(1:numberElemY,1:numberElemX) = volumenRatio;
	adaptPendCounter = 1;
	while changePerIteration > 0.01 && iteration <= maxIterations
        xold = x;
        if OnlyThermalIA == true
			x = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
			x = real(x);
        elseif OnlyStrucIA == true
			x = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
			x = real(x);
        elseif WeightDensIA == true
            xs = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            xs = real(xs);
            xt = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            xt = real(xt);
            x = weightFactorStruc*xs + (1-weightFactorStruc)* xt;
        elseif WeightSensIA == true
            x = coupled_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius, weightFactorStruc);
            x = real(x)
        elseif AdapStrucStartIA == true
            if changePhysType == false
			    x = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            else
                x = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            end
			x = real(x);
			# Adding old solution into the new one
			if addOldSolu == true
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						end
					end
				end		
			end
            # If changeiteration is reached, the old solution will be saved
            if iteration == adaptChangeIteration
                changePhysType = true
                addOldSolu = true
				xSelect = 0.9;			
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if x(ely,elx) >= xSelect
							xnew(ely,elx)   = 1.0;
						else
							xnew(ely,elx) = -1.0;
						end
					end
				end
                # Resetting all densitys which are not in the saved solution
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						else
							x(ely,elx) = volumenRatio;
						end
					end
				end	
                volumenRatio = adapVolFrac + volumenRatio
            end
        elseif AdapThermStartIA == true
            if changePhysType == false  
                x = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            else
                x = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            end
			x = real(x);
			# Adding old solution into the new one
			if addOldSolu == true
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						end
					end
				end		
			end
            # If changeiteration is reached, the old solution will be saved
            if iteration == adaptChangeIteration
                changePhysType == true
                addOldSolu = true
				xSelect = 0.9;			
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if x(ely,elx) >= xSelect
							xnew(ely,elx)   = 1.0;
						else
							xnew(ely,elx) = -1.0;
						end
					end
				end
                # Resetting all densitys which are not in the saved solution
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						else
							x(ely,elx) = volumenRatio;
						end
					end
				end	
                volumenRatio = adapVolFrac + volumenRatio
            end
        elseif ItAdapStrucStartIA  == true
            if changePhysType == false
			    x = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            else
                x = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            end
			x = real(x);
			# Adding old solution into the new one
			if addOldSolu == true
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						end
					end
				end		
			end
            # If changeiteration is reached, the old solution will be saved
            if iteration == adaptChangeIteration * adapCounter
                adapCounter = adapCounter + 1
                if changePhysType == false
                    changePhysType = true
                else
                    changePhysType = false
                end
                addOldSolu = true
				xSelect = 0.9;			
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if x(ely,elx) >= xSelect
							xnew(ely,elx)   = 1.0;
						else
							xnew(ely,elx) = -1.0;
						end
					end
				end
                # Resetting all densitys which are not in the saved solution
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						else
							x(ely,elx) = volumenRatio;
						end
					end
				end	
                volumenRatio = adapVolFrac + volumenRatio
            end
        elseif ItAdapThermStartIA == true
            if changePhysType == false
                x = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            else
			    x = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
            end
			x = real(x);
			# Adding old solution into the new one
			if addOldSolu == true
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						end
					end
				end		
			end
            # If changeiteration is reached, the old solution will be saved
            if iteration == adaptChangeIteration * adapCounter
                adapCounter = adapCounter + 1
                if changePhysType == false
                    changePhysType = true
                else
                    changePhysType = false
                end
                addOldSolu = true
				xSelect = 0.9;			
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if x(ely,elx) >= xSelect
							xnew(ely,elx)   = 1.0;
						else
							xnew(ely,elx) = -1.0;
						end
					end
				end
                # Resetting all densitys which are not in the saved solution
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						else
							x(ely,elx) = volumenRatio;
						end
					end
				end	
                volumenRatio = adapVolFrac + volumenRatio
            end
        elseif AdapWeighSensStrucStartIA == true
            if changePhysType == false  
                x = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
                x = real(x);
            else
                x = coupled_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius, weightFactorStruc);        
            end
			x = real(x);
			# Adding old solution into the new one
			if addOldSolu == true
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						end
					end
				end		
			end
            # If changeiteration is reached, the old solution will be saved
            if iteration == adaptChangeIteration
                changePhysType == true
                addOldSolu = true
				xSelect = 0.9;			
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if x(ely,elx) >= xSelect
							xnew(ely,elx)   = 1.0;
						else
							xnew(ely,elx) = -1.0;
						end
					end
				end
                # Resetting all densitys which are not in the saved solution
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						else
							x(ely,elx) = volumenRatio;
						end
					end
				end	
                volumenRatio = adapVolFrac + volumenRatio
            end
        elseif AdapWeighSensThermStartIA == true
            if changePhysType == false  
                x = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
                x = real(x)
            else
                x = coupled_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius, weightFactorStruc);
            end
			# Adding old solution into the new one
			if addOldSolu == true
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						end
					end
				end		
			end
            # If changeiteration is reached, the old solution will be saved
            if iteration == adaptChangeIteration
                changePhysType == true
                addOldSolu = true
				xSelect = 0.9;			
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if x(ely,elx) >= xSelect
							xnew(ely,elx)   = 1.0;
						else
							xnew(ely,elx) = -1.0;
						end
					end
				end
                # Resetting all densitys which are not in the saved solution
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						else
							x(ely,elx) = volumenRatio;
						end
					end
				end	
                volumenRatio = adapVolFrac + volumenRatio
            end
        elseif AdapWeighDensStrucStartIA == true
            if changePhysType == false  
                x = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
				x = real(x);
            else
		        xs = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
		        xs = real(xs);
		        xt = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
		        xt = real(xt);
		        x = weightFactorStruc*xs + (1-weightFactorStruc)* xt;
            end
			# Adding old solution into the new one
			if addOldSolu == true
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						end
					end
				end		
			end
            # If changeiteration is reached, the old solution will be saved
            if iteration == adaptChangeIteration
                changePhysType == true
                addOldSolu = true
				xSelect = 0.9;			
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if x(ely,elx) >= xSelect
							xnew(ely,elx)   = 1.0;
						else
							xnew(ely,elx) = -1.0;
						end
					end
				end
                # Resetting all densitys which are not in the saved solution
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						else
							x(ely,elx) = volumenRatio;
						end
					end
				end	
                volumenRatio = adapVolFrac + volumenRatio
            end
        elseif AdapWeighDensThermStartIA == true
            if changePhysType == false  
                x = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
				x = real(x);
            else
		        xs = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
		        xs = real(xs);
		        xt = thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius);
		        xt = real(xt);
		        x = weightFactorStruc*xs + (1-weightFactorStruc)* xt;
            end
			# Adding old solution into the new one
			if addOldSolu == true
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						end
					end
				end		
			end
            # If changeiteration is reached, the old solution will be saved
            if iteration == adaptChangeIteration
                changePhysType == true
                addOldSolu = true
				xSelect = 0.9;			
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if x(ely,elx) >= xSelect
							xnew(ely,elx)   = 1.0;
						else
							xnew(ely,elx) = -1.0;
						end
					end
				end
                # Resetting all densitys which are not in the saved solution
				for ely = 1:numberElemY
					for elx = 1:numberElemX
						if xnew(ely,elx) > 0
							x(ely,elx) = xnew(ely,elx);
						else
							x(ely,elx) = volumenRatio;
						end
					end
				end	
                volumenRatio = adapVolFrac + volumenRatio
            end
        end
		iteration = iteration + 1;
		# Output of the results
		changePerIteration = max(max(abs(x-xold)));
  		fprintf(' It.:%5i ch.:%7.3f\n',iteration,changePerIteration);
		# Graphical plot
		#try
		colormap(gray); imagesc(-real(x)); axis equal; axis tight; axis off;pause(1e-6);
		#catch
		#	fprintf('Picture could not be printed\n');
		#end
	end
end

#-----
# Coupled sensitivity
#-----
function [xst] = coupled_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius, weightFactorStruc)
	# Calculating the system answer (displacements)
	[U]=FE(numberElemX,numberElemY,x,penaltyExponent);
	# Sensitivity Analysis
	[KE] = lk;
	c = 0.;
	for ely = 1:numberElemY
		for elx = 1:numberElemX
			n1 = (numberElemY+1)*(elx-1)+ely;
			n2 = (numberElemY+1)* elx +ely;
			Ue = U([2*n1-1;2*n1; 2*n2-1;2*n2; 2*n2+1; 2*n2+2; 2*n1+1;2*n1+2],1);
			c = c + x(ely,elx)^penaltyExponent*Ue'*KE*Ue;
			dcS(ely,elx) = -penaltyExponent*x(ely,elx)^(penaltyExponent-1)*Ue'*KE*Ue;			
		end
	end
	# Calculating the system answer (temperatures)
	[U]=FET(numberElemX,numberElemY,x,penaltyExponent);
	# Sensitivity Analysis
	[KE] = lkT;
	c = 0.;
	for ely = 1:numberElemY
		for elx = 1:numberElemX
			n1 = (numberElemY+1)*(elx-1)+ely;
			n2 = (numberElemY+1)* elx +ely;
			Ue = U([n1;n2;n2+1;n1+1],1);
			c = c + (0.001+0.999*x(ely,elx)^penaltyExponent)*Ue'*KE*Ue;
			dcT(ely,elx) = -0.999*penaltyExponent*x(ely,elx)^(penaltyExponent-1)*Ue'*KE*Ue;
		end
	end
	normS = sum(mean(abs(dcS)))/(numberElemX*numberElemY);
	normT = sum(mean(abs(dcT)))/(numberElemX*numberElemY);
	#b = mean(abs(dcT))
	dc = 1/normS*dcS *weightFactorStruc + 1/normT*dcT * (1-weightFactorStruc);
	# Filtering the sensitivitys
	[dc] = check(numberElemX,numberElemY,minFilterRadius,x,dc);
	# Using MMA-Method for the new densitiy scaleing 
	# so that the ristriction will taken into account
	[xst] = OC(numberElemX,numberElemY,x,volumenRatio,dc);
end
#-----
# Structural Calculation
#-----
function [xs] = structural_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius)
	# Calculating the system answer (displacements)
	[U]=FE(numberElemX,numberElemY,x,penaltyExponent);
	# Sensitivity Analysis
	[KE] = lk;
	c = 0.;
	for ely = 1:numberElemY
		for elx = 1:numberElemX
			n1 = (numberElemY+1)*(elx-1)+ely;
			n2 = (numberElemY+1)* elx +ely;
			Ue = U([2*n1-1;2*n1; 2*n2-1;2*n2; 2*n2+1; 2*n2+2; 2*n1+1;2*n1+2],1);
			c = c + x(ely,elx)^penaltyExponent*Ue'*KE*Ue;
			dc(ely,elx) = -penaltyExponent*x(ely,elx)^(penaltyExponent-1)*Ue'*KE*Ue;			
		end
	end
	# Filtering the sensitivitys
	[dc] = check(numberElemX,numberElemY,minFilterRadius,x,dc);
	# Using MMA-Method for the new densitiy scaleing 
	# so that the ristriction will taken into account
	[xs] = OC(numberElemX,numberElemY,x,volumenRatio,dc);

end
#-----
# Thermal Calculation
#-----
function [xt]=thermal_topo(numberElemX,numberElemY,x,volumenRatio,penaltyExponent,minFilterRadius)
	# Calculating the system answer (temperatures)
	[U]=FET(numberElemX,numberElemY,x,penaltyExponent);
	# Sensitivity Analysis
	[KE] = lkT;
	c = 0.;
	for ely = 1:numberElemY
		for elx = 1:numberElemX
			n1 = (numberElemY+1)*(elx-1)+ely;
			n2 = (numberElemY+1)* elx +ely;
			Ue = U([n1;n2;n2+1;n1+1],1);
			c = c + (0.001+0.999*x(ely,elx)^penaltyExponent)*Ue'*KE*Ue;
			dc(ely,elx) = -0.999*penaltyExponent*x(ely,elx)^(penaltyExponent-1)*Ue'*KE*Ue;
		end
	end			
	# Filtering the sensitivitys
	[dc] = check(numberElemX,numberElemY,minFilterRadius,x,dc);
	# Using MMA-Method for the new densitiy scaleing 
	# so that the ristriction will taken into account
	[xt] = OC(numberElemX,numberElemY,x,volumenRatio,dc);
end
#----
# Optimization criteria solved by using moving athemthodes
#---
function [xnew]=OC(numberElemX,numberElemY,x,volumenRatio,dc)
	l1 = 0; l2 = 100000; move = 0.2;
	while (l2-l1 > 1e-4)
		lmid = 0.5*(l2+l1);
		xnew = max(0.001,max(x-move,min(1.,min(x+move,x.*sqrt(-dc./lmid)))));
        #new = max(0.001, sign(dc-lmid))
		if sum(sum(xnew)) - volumenRatio*numberElemX*numberElemY > 0;
			l1 = lmid;
		else
			l2 = lmid;
		end
	end
end
#----
# Structural and thermal filter
#---
function [dcn]=check(numberElemX,numberElemY,minFilterRadius,x,dc)
	dcn=zeros(numberElemY,numberElemX);
	for i = 1:numberElemX
		for j = 1:numberElemY
			sum=0.0;
			for k = max(i-round(minFilterRadius),1): min(i+round(minFilterRadius),numberElemX)
				for l = max(j-round(minFilterRadius),1): min(j+round(minFilterRadius), numberElemY)
					fac = minFilterRadius-sqrt((i-k)^2+(j-l)^2);
					sum = sum+max(0,fac);
					#dcn(j,i) = dcn(j,i) + max(0,fac)*x(l,k) *dc(l,k);
					dcn(j,i) = dcn(j,i) + max(0,fac) *dc(l,k);
				end
			end
			#dcn(j,i) = dcn(j,i)/(x(j,i)*sum);
			dcn(j,i) = dcn(j,i)/(sum);
		end
	end
end
#----
# Structural analysis (FEM)
#---
function [U]=FE(numberElemX,numberElemY,x,penaltyExponent)
	[KE] = lk;
	K = sparse(2*(numberElemX+1)*(numberElemY+1), 2*(numberElemX+1)*(numberElemY+1));
	F = sparse(2*(numberElemY+1)*(numberElemX+1),-1); U = sparse(2*(numberElemY+1)*(numberElemX+1),1);
	for ely = 1:numberElemY
		for elx = 1:numberElemX
			n1 = (numberElemY+1)*(elx-1)+ely;
			n2 = (numberElemY+1)* elx +ely;
			edof = [2*n1-1; 2*n1; 2*n2-1; 2*n2; 2*n2+1; 2*n2+2;2*n1+1; 2*n1+2];
			K(edof,edof) = K(edof,edof) + x(ely,elx)^penaltyExponent*KE;
		end
	end
	% DEFINE LOADSAND SUPPORTS(HALF MBB-BEAM)
	F(2,1) = -1;
	fixeddofs = union([1:2:2*(numberElemY+1)],[2*(numberElemX+1)*(numberElemY+1)]);
	alldofs = [1:2*(numberElemY+1)*(numberElemX+1)];
	freedofs = setdiff(alldofs,fixeddofs);
	% SOLVING 127
	U(freedofs,:) = K(freedofs,freedofs) \F(freedofs,:);
	U(fixeddofs,:)= 0;
end
#----
# Thermal analysis (FEM)
#---
function [U]=FET(numberElemX,numberElemY,x,penaltyExponent)
	[KE] = lkT;
	K = sparse((numberElemX+1)*(numberElemY+1),(numberElemX+1)*(numberElemY+1));
	F = sparse((numberElemY+1)*(numberElemX+1),1); U = sparse((numberElemY+1)*(numberElemX+1),1);
	for ely = 1:numberElemY
		for elx = 1:numberElemX
			n1 = (numberElemY+1)*(elx-1)+ely;
			n2 = (numberElemY+1)* elx +ely;
			edof = [n1; n2; n2+1; n1+1];
			K(edof,edof) = K(edof,edof) + (0.001+0.999*x(ely,elx)^penaltyExponent)*KE;
		end
	end
	% DEFINE LOADSAND SUPPORTS(HALF MBB-BEAM)
	F(:,1) = -0.01;
	fixeddofs = [numberElemY/2+1-(numberElemY/20):numberElemY/2+1+(numberElemY/20)];
	alldofs = [1:(numberElemY+1)*(numberElemX+1)];
	freedofs = setdiff(alldofs,fixeddofs);
	U(freedofs,:) = K(freedofs,freedofs) \F(freedofs,:);
	U(fixeddofs,:)= 0;
end
#----
# Element stiffnes matrix
#---
function [KE]=lk
	E = 1.;
	nu = 0.3;
	k=[ 1/2-nu/6 1/8+nu/8 -1/4-nu/12 -1/8+3*nu/8 ...
	-1/4+nu/12 -1/8-nu/8 nu/6 1/8-3*nu/8];
	KE = E/(1-nu^2)* [ k(1) k(2) k(3) k(4) k(5) k(6) k(7) k(8)
	 k(2) k(1) k(8) k(7) k(6) k(5) k(4) k(3)
	 k(3) k(8) k(1) k(6) k(7) k(4) k(5) k(2)
	 k(4) k(7) k(6) k(1) k(8) k(3) k(2) k(5)
	 k(5) k(6) k(7) k(8) k(1) k(2) k(3) k(4)
	 k(6) k(5) k(4) k(3) k(2) k(1) k(8) k(7)
	 k(7) k(4) k(5) k(2) k(3) k(8) k(1) k(6)
	 k(8) k(3) k(2) k(5) k(4) k(7) k(6) k(1)];
end
#----
# Element heating exchange matrix
#---
function [KE]=lkT

	KE = [2/3 -1/6 -1/3 -1/6
		  -1/6 2/3 -1/6 -1/3
		  -1/3 -1/6 2/3 -1/6
		  -1/6 -1/3 -1/6 2/3];
end
multi_topo(40,20,0.4,3.0,2.0,20,0.2,6,0.5,1,1,1,0,0,0,0)