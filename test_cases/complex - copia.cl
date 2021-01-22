class Main inherits IO {
    main() : SELF_TYPE {
	(let c : AUTO_TYPE <- (new Complex).init(1, 1) in
	    if c.reflect_X().reflect_Y() = c.reflect_0()
	    then out_string("=)\n")
	    else out_string("=(\n")
	    fi
	)
    };
};

class Complex inherits IO {
    x : AUTO_TYPE;
    y : AUTO_TYPE;

    init(a : Int, b : Int) : AUTO_TYPE {
	{
	    x <- a;
	    y <- b;
	    self;
	}
    };

    print() : Object {
	if y = 0
	then out_int(x)
	else out_int(x).out_string("+").out_int(y).out_string("I")
	fi
    };

    reflect_0() : AUTO_TYPE {
	{
	    x <- ~x;
	    y <- ~y;
	    self;
	}
    };

    reflect_X() : AUTO_TYPE {
	{
	    y <- ~y;
	    self;
	}
    };

    reflect_Y() : AUTO_TYPE {
	{
	    x <- ~x;
	    self;
	}
    };
};
