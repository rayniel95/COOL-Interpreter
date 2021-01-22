-- example of static and dynamic type differing for a dispatch

Class Book inherits IO {
    title : AUTO_TYPE;
    author : AUTO_TYPE;

    initBook(title_p : String, author_p : String) : AUTO_TYPE {
        {
            title <- title_p;
            author <- author_p;
            self;
        }
    };

    print() : AUTO_TYPE {
        {
            out_string("title:      ").out_string(title).out_string("\n");
            out_string("author:     ").out_string(author).out_string("\n");
            self;
        }
    };
};

Class Article inherits Book {
    per_title : AUTO_TYPE;

    initArticle(title_p : String, author_p : String,
		per_title_p : String) : AUTO_TYPE {
        {
            initBook(title_p, author_p);
            per_title <- per_title_p;
            self;
        }
    };

    print() : Book {
        {
	    self@Book.print();
            out_string("periodical:  ").out_string(per_title).out_string("\n");
            self;
        }
    };
};

Class BookList inherits IO { 
    (* Since abort "returns" type Object, we have to add
       an expression of type Bool here to satisfy the typechecker.
       This code is unreachable, since abort() halts the program.
    *)
    isNil() : AUTO_TYPE { { abort(); true; } };
    
    cons(hd : Book) : AUTO_TYPE {
        (let new_cell : AUTO_TYPE <- new Cons in
            new_cell.init(hd,self)
        )
    };

    (* Since abort "returns" type Object, we have to add
       an expression of type Book here to satisfy the typechecker.
       This code is unreachable, since abort() halts the program.
    *)
    car() : AUTO_TYPE { { abort(); new Book; } };
    
    (* Since abort "returns" type Object, we have to add
       an expression of type BookList here to satisfy the typechecker.
       This code is unreachable, since abort() halts the program.
    *)
    cdr() : AUTO_TYPE { { abort(); new BookList; } };
    
    print_list() : AUTO_TYPE { abort() };
};

Class Cons inherits BookList {
    xcar : Book;  -- We keep the car and cdr in attributes.
    xcdr : BookList; -- Because methods and features must have different names,
    -- we use xcar and xcdr for the attributes and reserve
    -- car and cdr for the features.
    
    isNil() : AUTO_TYPE { false };
    
    init(hd : Book, tl : BookList) : Cons {
        {
            xcar <- hd;
            xcdr <- tl;
            self;
        }
    };

    car() : Book { xcar };

    cdr() : BookList { xcdr };
    
    print_list() : Object {
        {
            case xcar.print() of
                dummy : Book => out_string("- dynamic type was Book -\n");
                dummy : Article => out_string("- dynamic type was Article -\n");
            esac;
            xcdr.print_list();
        }
    };
};

Class Nil inherits BookList {
    isNil() : Bool { true };

    print_list() : Object { true };
};


Class Main {

    books : BookList;

    main() : Object {
        (let a_book : Book <-
            (new Book).initBook("Compilers, Principles, Techniques, and Tools",
                                "Aho, Sethi, and Ullman")
        in
            (let an_article : Article <-
                (new Article).initArticle("The Top 100 CD_ROMs",
                                          "Ulanoff",
                                          "PC Magazine")
            in
                {
                    books <- (new Nil).cons(a_book).cons(an_article);
                    books.print_list();
                }
            )  -- end let an_article
        )  -- end let a_book
    };
};
