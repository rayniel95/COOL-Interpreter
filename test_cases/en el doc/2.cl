class Main inherits IO { 
    main() : AUTO_TYPE { 
        {
        let x : AUTO_TYPE <- 3 + 2 in { 
            case x of y : Int => out_string("Ok"); esac; 
        };
        } 
    };
    succ(n : AUTO_TYPE) : AUTO_TYPE { n + 1 };  
    fact(n : AUTO_TYPE) : AUTO_TYPE { if (n<0) then 1 else n*fact(n-1) fi };
    step(p : AUTO_TYPE) : AUTO_TYPE { p.init(1,1) };
    ackermann(m : AUTO_TYPE, n: AUTO_TYPE) : AUTO_TYPE { 
        if (m==0) then n+1 else 
            if (n==0) then ackermann(m-1, 1) else 
                ackermann(m-1, ackermann(m, n-1)) 
            fi 
        fi 
    };
};

class Point { 
    x : AUTO_TYPE; 
    y : AUTO_TYPE;
    init(n : Int, m : Int) : SELF_TYPE { 
        { 
            x <- n; 
            y <- m; 
            self;
            }
    };

};



