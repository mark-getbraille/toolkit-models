"""Common English first names, used by scrub.py to find people's names in a message so they can be replaced with a
placeholder such as [Name]. The list is made by hand from the most common given names in the United States and other
English-speaking countries; it is only a helper: names in a message's own headers, greetings and signatures are
found as well (see scrub.py), and every name the kit finds is replaced, public or private.

Words that are also ordinary English words (Will, May, Bill, Mark, Grace, Rose, June, Hope, Faith, Joy, Art, Pat,
Sue, Rich, Frank, Don, Ray, Chase, Hunter, Summer, Dawn, Penny, Ruby, Jack ...) are in AMBIGUOUS: they count as a name
only next to another name, after a greeting, before a sign-off, or with a title (Mr, Ms, Dr ...).
"""

FIRST_NAMES = set("""
aaron abby abigail adam adrian adrienne aimee al alan albert alex alexa alexander alexandra alexis alfred alice
alicia alison allan allen allison alma alvin amanda amber amelia amy ana andre andrea andrew andy angela angelica
angie anita ann anna anne annette annie anthony antonio april arlene arnold arthur ashley audrey austin barbara
barry beatrice becky ben benjamin bernard bernice beth betsy betty beverly bill billy blake bobbie bobby bonnie
brad bradley brandon brandy brenda brent brett brian bridget brittany brooke bruce bryan byron caleb calvin cameron
carl carla carlos carmen carol carole caroline carolyn carrie casey cassandra catherine cathy cecil chad charlene
charles charlie charlotte chelsea cheryl chris christian christina christine christopher christy cindy claire
clara clarence claudia clayton clifford clint clyde cody colin colleen connie constance corey courtney craig
crystal curtis cynthia daisy dale dan dana daniel danielle danny darlene darrell darren daryl dave david dean
debbie deborah debra denise dennis derek derrick diana diane dianne dolores donald donna doris dorothy doug douglas
duane dustin dwayne dylan earl eddie edgar edith edna eduardo edward edwin eileen elaine eleanor elena elijah
elizabeth ella ellen elmer eloise emily emma eric erica erik erin ernest esther ethan ethel eugene eva evan evelyn
everett felicia felix fernando florence floyd frances francis francisco fred freda freddie frederick gabriel
gabrielle gail gary gavin gene geneva geoffrey george georgia gerald geraldine gilbert gina giovanni glen glenda
glenn gloria gordon greg gregory gwendolyn hannah harold harriet harry harvey hazel heather hector heidi helen
henry herbert herman hilda holly howard ian ida irene isaac isabel isabella jacob jacqueline jaime jake james
jamie jan jane janet janice jared jasmine jason jay jean jeanette jeanne jeff jeffery jeffrey jenna jennifer
jenny jeremy jerome jerry jesse jessica jessie jill jim jimmy jo joan joann joanna joanne jodi jody joe joel
johanna john johnny jon jonathan jordan jorge jose joseph josephine josh joshua joyce juan juanita judith judy
julia julian julie justin kara karen kari karl kate katherine kathleen kathryn kathy katie katrina kay kayla
keith kelly kelsey ken kendra kenneth kenny kerry kevin kim kimberly kirk kristen kristin kristina kristy kurt
kyle lana lance larry laura lauren laurie lawrence leah lee leigh lena leo leon leonard leroy leslie lester
lillian linda lindsay lindsey lisa lloyd logan lois lonnie loretta lori lorraine louis louise lucas lucille lucy
luis luke lydia lynda lynn lynne mabel madeline madison mae malcolm mandy manuel marc marcia marcus margaret
margie maria marian marianne marie marilyn mario marion marjorie marlene marsha marshall martha martin marvin mary
mason matt matthew maureen maurice max maxine megan melanie melinda melissa melody melvin meredith mia michael
micheal michele michelle miguel mike mildred milton miranda miriam misty mitchell molly monica monique morgan
myrtle nancy naomi natalie natasha nathan nathaniel neil nellie nelson nicholas nichole nick nicole nina noah
noel nora norma norman olga olivia oscar pam pamela patricia patrick patsy patti patty paul paula pauline pedro
peggy perry peter phil philip phillip phyllis priscilla rachel rafael ralph ramon randall randy raymond rebecca
regina reginald rene renee rhonda ricardo richard rick ricky rita robert roberta roberto robin robyn rodney
roger roland ron ronald ronnie rosa rosemary ross roy ruben russell ruth ryan sabrina sally sam samantha samuel
sandra sandy sara sarah scott sean sergio seth shane shannon sharon shawn sheila shelby shelley sheri sherri
sherry shirley sidney sophia stacey stacy stanley stella stephanie stephen steve steven stuart susan suzanne
sylvia tamara tammy tanya tara ted teresa terri terry thelma theodore theresa thomas tiffany tim timothy tina
toby todd tom tommy toni tony tonya tracey traci tracy travis trevor troy tyler valerie vanessa vera vernon
veronica vicki vickie vicky victor victoria vincent viola virginia vivian wade walter wanda warren wayne wendy
wesley whitney wilbur willard william willie wilma winston yolanda yvette yvonne zachary zoe
vince kristi kristie marla shari tricia trish jenifer jodie lorie dee deb steph liz beth becca kat kim jen
stan hal mitch rod gus ned abe cal les randi twanda jennie kristian gerry natalia alina gwyn greg jerr jeff mo
louise kay vickie geir sherron rosalee hunter tana sara susie suzy sonia sabra lindy lorna lynette dorothea kurt
vladimir sergei ivan dmitri olga svetlana pierre jacques francois hans juergen klaus ahmed mohammed fatima priya raj
ravi amit anil sanjay vijay sunil deepak arun kumar wei li ming chen hiroshi yuki kenji akira takeshi carlos javier
alejandro diego pablo lucia sofia valentina camila mateo santiago ana isabella giulia marco luca giovanni francesca
""".split())

AMBIGUOUS = set("""
will may bill mark grace rose june hope faith joy art pat sue rich frank don ray chase hunter summer dawn penny
ruby jack april august autumn bob guy rob gene sandy ed al lee jay dean jo carol eve iris ivy lily olive pearl
robin rusty stone wade victor king major miles price rich sterling young jan christian georgia virginia
dick ginger drew rod jean bud chip buck duke
florence austin jordan charlotte madison chelsea sidney carmen
""".split())

FIRST_NAMES -= AMBIGUOUS

# Titles that make the next capitalised word a name: "Mr Jones", "Dr. Patel".
TITLES = ["Mr", "Mrs", "Ms", "Miss", "Mx", "Dr", "Prof", "Professor", "Sir", "Madam", "Rev", "Senator", "Governor",
          "Gov", "Rep", "Representative", "Mayor", "Judge", "Commissioner", "Secretary", "President", "Chairman"]

# Common surnames (from the most frequent surnames in the United States and Britain), replaced wherever they are
# written with a capital letter. Surnames that are also ordinary words (Brown, White, Green, Young, King, Hill, Wood,
# Rich, Lay, Black, Gray, Long, Price, Rice, Hunt, Bush ...) count as a name when capitalised in the middle of a
# sentence.
SURNAMES = set("""
smith johnson williams jones garcia miller davis rodriguez martinez hernandez lopez gonzalez wilson anderson thomas
taylor moore jackson martin thompson harris sanchez clark ramirez lewis robinson walker allen wright scott torres
nguyen flores adams nelson baker hall rivera campbell mitchell carter roberts gomez phillips evans turner diaz parker
cruz edwards collins reyes stewart morris morales murphy cook rogers gutierrez ortiz morgan cooper peterson bailey
reed kelly howard ramos kim cox ward richardson watson brooks chavez bennett gray mendoza ruiz hughes alvarez
castillo sanders patel myers ross foster jimenez powell jenkins perry russell sullivan bell coleman butler henderson
barnes gonzales fisher vasquez simmons romero jordan patterson alexander hamilton graham reynolds griffin wallace
moreno west cole hayes bryant herrera gibson ellis tran medina aguilar stevens murray ford castro marshall owens
harrison fernandez mcdonald woods washington kennedy wells vargas henry chen freeman webb tucker guzman burns crawford
olson simpson porter hunter gordon mendez silva shaw snyder mason dixon munoz hunt hicks holmes palmer wagner black
robertson boyd rose stone salazar fox warren mills meyer rice schmidt garza daniels ferguson nichols stephens soto
weaver ryan gardner payne grant dunn kelley spencer hawkins arnold pierce vazquez hansen peters santos hart bradley
knight elliott cunningham duncan armstrong hudson carroll lane riley andrews alvarado ray delgado berry perkins
hoffman johnston matthews pena richards contreras willis carpenter lawrence sandoval guerrero george chapman rios
estrada ortega watkins greene nunez wheeler valdez harper burke larson santiago maldonado morrison franklin carlson
austin dominguez carr lawson jacobs obrien lynch singh vega bishop montgomery oliver jensen harvey williamson gilbert
dean sims espinoza howell li wong reid hanson le mccoy garrett burton fuller wang weber welch rojas lucas marquez
fields park yang little banks padilla day walsh bowman schultz luna fowler mejia davidson acosta brewer may holland
juarez newman pearson curtis cortez douglas schneider joseph barrett navarro figueroa keller avila wade molina
stanley hopkins campos barnett bates chambers caldwell beck lambert miranda byrd craig ayala lowe frazier powers neal
leonard gregory carrillo sutton fleming rhodes shelton schwartz norris jennings watts duran walters cohen mcdaniel
moran parks steele vaughn becker holt deleon barker terry hale leon hail benson haynes horton miles lyons pham graves
bush thornton wolfe warner cabrera mckinney mann zimmerman dawson lara fletcher page mccarthy love robles cervantes
solis erickson reeves chang klein salinas fuentes baldwin daniel simon velasquez hardy higgins aguirre lin cummings
chandler sharp barber bowen ochoa dennis robbins liu ramsey francis griffith paul blair oconnor cardenas pacheco
cross calderon quinn moss swanson chan rivas khan rodgers serrano fitzgerald rosales stevenson christensen manning
gill curry mclaughlin harmon mcgee gross doyle garner newton burgess reese walton blake trujillo adkins brady
goodman roman webster goodwin fischer huang potter delacruz montoya todd wu hines mullins castaneda malone cannon
tate mack sherman hubbard hodges zhang guerra wolf valencia saunders franco rowe gallagher farmer hammond hampton
townsend ingram wise gallegos clarke barton schroeder maxwell waters logan camacho strickland norman person colon
parsons frank harrington glover osborne buchanan casey floyd patton ibarra ball tyler suarez bowers orozco salas
cobb gibbs andrade bauer conner moody escobar mcguire lloyd mueller hartman french kramer mcbride pope lindsey
velazquez norton mccormick sparks flynn yates hogan marsh macias villanueva zamora pratt stokes owen ballard lang
brock villarreal charles drake barrera cain patrick pineda burnett mercado santana shepherd bautista ali shaffer
lamb trevino mckenzie hess beil olsen cochran morton nash wilkins petersen briggs shah roth nicholson holloway
lozano rangel flowers hoover short arias mora valenzuela bryan meyers weiss underwood bass greer summers houston
carson morrow clayton whitaker decker yoder collier zuniga carey wilcox melendez poole roberson larsen conley davenport
copeland massey lam huff rocha cameron jefferson hood monroe anthony pittman huynh randall singleton kirk combs mathis
christian skinner bradford richard galvan wall boone kirby wilkinson bridges bruce atkinson velez meza roy vincent
york hodge villa abbott allison tapia gates chase sosa sweeney farrell wyatt dalton horn barron phelps yu dickerson
heath foley atkins mathews bonilla acevedo benitez zavala hensley glenn cisneros harrell shields rubio choi huffman
boyer garrison arroyo bond kane hancock callahan dillon cline wiggins grimes arellano melton oneill savage ho beltran
pitts parrish ponce rich booth koch golden ware brennan mcdowell marks cantu humphrey baxter sawyer clay tanner
hutchinson kaur berg wiley gilmore russo villegas hobbs keith wilkerson ahmed beard mcclain montes mata rosario vang
walter henson oneal mosley mcclure beasley stephenson snow huerta preston vance barry johns eaton blackwell dyer
prince macdonald solomon guevara stafford english hurst woodard cortes shannon kemp nolan mccullough merritt murillo
moon salgado strong kline cordova barajas roach rosas winters jacobson lester knox bullock kerr leach meadows orr
davila whitehead pruitt kent conway mckee barr david dejesus marin berger mcintyre blankenship gaines palacios cuevas
bartlett durham dorsey mccall odonnell stein browning stout lowery sloan mclean hendricks calhoun sexton chung gentry
hull duarte ellison nielsen gillespie buck middleton sellers leblanc esparza hardin bradshaw mcintosh howe livingston
frost glass morse knapp herman stark bravo noble spears weeks corona frederick buckley mcfarland hebert enriquez
hickman quintero randolph schaefer walls trejo house reilly pennington michael conrad giles benjamin crosby fitzpatrick
donovan mays mahoney valentine raymond medrano hahn mcmillan small bentley felix peck lucero boyle hanna pace rush
hurley harding mcconnell bernal nava ayers everett ventura avery pugh mayer bender shepard mcmahon landry case sampson
moses magana blackburn dunlap gould duffy vaughan herring mckay espinosa rivers farley bernard ashley friedman potts
truong costa correa blevins nixon clements fry delarosa best benton lugo portillo dougherty crane haley phan villalobos
blanchard horne finley quintana lynn esquivel bean dodson mullen xiong hayden cano levy huber richmond moyer lim frye
sheppard mccarty avalos booker waller parra woodward jaramillo krueger rasmussen brandt peralta donaldson stuart
faulkner maynard galindo coffey estes sanford burch maddox vo oconnell vu andersen spence mcpherson church schmitt
stanton leal cherry compton dudley sierra pollard alfaro hester proctor lu hinton novak good madden mccann terrell
jarvis dickson reyna cantrell mayo branch hendrix rollins rowland whitney duke odom daugherty travis tang archer
skilling whalley lay fastow kopper delainey frevert kitchen lavorato shankman buy
""".split())

# Ambiguous first names that are also months: never a name at the start of a sentence or before a number.
MONTHLIKE = {"may", "june", "april", "august", "will", "hope", "grace", "joy", "faith"}


def _load_wordlists():
    """(common, public) from wordlists.json beside this file (made by make_wordlists.py); empty sets if missing."""
    import json
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordlists.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return set(data["common"]), set(data["public"])
    except (OSError, ValueError, KeyError):
        return set(), set()


# Public place names, holidays and the like added by hand to the "public" list (never people).
EXTRA_PUBLIC = set("""
Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia Hawaii Idaho Illinois
Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota Mississippi Missouri Montana
Nebraska Nevada Hampshire Jersey Mexico York Carolina Dakota Ohio Oklahoma Oregon Pennsylvania Rhode Tennessee Texas
Utah Vermont Virginia Washington Wisconsin Wyoming Houston Dallas Austin Portland Chicago Boston Denver Seattle
Phoenix Atlanta Miami Detroit Omaha Calgary Toronto Vancouver Montreal Ottawa London Paris Berlin Tokyo Sydney
Francisco Diego Angeles Vegas Orleans Antonio Louis Sacramento Philadelphia Pittsburgh Cleveland Baltimore Tulsa
Canada Mexico Europe Asia Africa America American Canadian British English French German Spanish Japanese Chinese
Christmas Thanksgiving Easter Halloween Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February
March April May June July August September October November December Enron Internet Web Email Mon Tue Wed Thu Fri
Sat Sun Jan Feb Mar Apr Jun Jul Aug Sep Sept Oct Nov Dec Pacific Atlantic Gulf Northwest Southwest Midwest
""".split())

COMMON_WORDS, PUBLIC_NAMES = _load_wordlists()
PUBLIC_NAMES |= EXTRA_PUBLIC
