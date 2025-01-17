function codes = matpower_gen_type (types)
    n = size(types)(1);
    codes = zeros (1,n)';
    for i=1:n
        code = strcat(types{i});
        if (strcmp(code, 'PV') == 1)
            codes(i) = 1;
        endif
        if (strcmp(code, 'WT') == 1)
            codes(i) = 2;
        endif
    endfor
endfunction

