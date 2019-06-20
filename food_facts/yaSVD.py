import math
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def dropFeatures(df, min_rows=30):
    '''Ingests a dataframe and required number of data per feature.
    Returns dataframe with dropped features with less than the required number of rows'''
    #takes counts of features and finds those that don't meet our threshold
    features_drop = df.transpose()[df.applymap(lambda x: 0 if math.isnan(x) else 1).sum(axis=0)<min_rows].index
    return df.drop(features_drop, axis=1)   

def plotRandomFeatures(df):
    'Ingest a dataframe and return 9 random distribution plots of its features'
    #choose 9 random features to plot
    rand_nutrients = df.sample(n=9,replace=False,axis=1)
    # set figure size to span notebook
    plt.rcParams['figure.figsize']=(20,10)
    #set layout of graphs as a 3X3
    fig, ((ax1, ax2, ax3),
      (ax4, ax5, ax6),
      (ax7, ax8, ax9)) = plt.subplots(nrows=3, ncols=3, sharey=False)
    #plot one distribution at a time, ignorming the NANs
    sns.distplot(rand_nutrients.ix[:,0].dropna(), ax=ax1,)
    sns.distplot(rand_nutrients.ix[:,1].dropna(), ax=ax2,)
    sns.distplot(rand_nutrients.ix[:,2].dropna(), ax=ax3,)
    sns.distplot(rand_nutrients.ix[:,3].dropna(), ax=ax4,)
    sns.distplot(rand_nutrients.ix[:,4].dropna(), ax=ax5,)
    sns.distplot(rand_nutrients.ix[:,5].dropna(), ax=ax6,)
    sns.distplot(rand_nutrients.ix[:,6].dropna(), ax=ax7,)
    sns.distplot(rand_nutrients.ix[:,7].dropna(), ax=ax8,)
    sns.distplot(rand_nutrients.ix[:,8].dropna(), ax=ax9,)
    #add an overall plot title
    fig.suptitle('Random Sample of Histograms of the Features');

def calcConverge(df1,df2):
    #the norm of the difference is error. 
    #Divide the error by the norm of the original matrix to get RSS
   	return np.linalg.norm(df1 - df2)/np.linalg.norm(df1)

def approxMatrix(U,s,V,rank):
	'Returns a similar matrix to our original matrix, but or lower rank'
	#truncate the rows of V
	Vr = V[:rank,:]
	#truncate the columns of U
	Ur = U[:,:rank]
	#make s a diagonal matrix
	sd = np.diag(s)
	#make sigma corresond to new truncated matrix size
	sr = sd[0:rank,0:rank]
	#create the new similar matrix
	return Ur.dot(sr.dot(Vr))

def SVDImpute(df, rank=20, threshold=.001, iterations=200):
    '''ingests dataframe with NaNs, a desired convergence threshold for error,
    as well as a maximum number of iterations allowed. Uses SVD to simultaneously impute fill all NaNs.
    Returns a normalized, imputed matrix, with the number of iterations and final error'''
    nan_loc = np.argwhere(np.isnan(df.values))
    
    #fill with the average of the column
    df = df.fillna(df.mean())

    #df = preprocessing.scale(df) #we will choose to scale later; it's bad practice to do both in one function
    #set error to one so that while loop runs
    
    fake_error = 1

    #start counting your iterations
    counter = 0

    while fake_error > threshold:
        #run the first SVD iteration
        #print("started iteration in while loop {}".format(counter))
        U, s, V = np.linalg.svd(df, full_matrices=False)

        #build up our similar matrix using SVD
        Ar = approxMatrix(U,s,V,rank=rank)
        
        #assess whether matrix has converged:
        fake_error = calcConverge(df,Ar)
        
        #save the actual error for printing to output
        error = fake_error
        
        #the rows corresponding with NAN
        rows = nan_loc.T[0]
        #the columns corresponding with NAN
        cols = nan_loc.T[1]
        #replace the old NAN values with the new NAN values
        df.values[rows,cols] = Ar[rows,cols]
        
        #add 1 to your iterator
        counter += 1

        if counter == iterations:
            #if we hit our max iterations, force the while loop to stop by setting fake_error to some tiny value
            fake_error = threshold - (threshold/2)
            
    print("number of iterations: {}, final error: {}".format(counter,error))
    return df

def compareComponents(df,c1,c2):
    '''Ingests a dataframe and the index of the two components that will be plotted. Returns a plot to exhamine
    the differences between the two components'''
    U, s, V = np.linalg.svd(df, full_matrices=False)
    plt.rcParams['figure.figsize']=(10,10)
    #project the data into the new space
    X = df.values.dot(V[c1])
    #project the data once more
    Y = df.values.dot(V[c2])
    plt.scatter(X, Y)
    plt.show()

def plotComponentParallelCoordinates(df, components=5, features=10):
    '''ingests a noramlized dataframe, runs SVD to get 
    the top corresponding components and plots parallel plot of the differences'''
    U, s, V = np.linalg.svd(df, full_matrices=False)

    plt.rcParams['figure.figsize']=(20,10)
    
    #for every column in V, we want to create a title
    names = ["Component{}".format(n) for n in range(V.shape[1])]
    
    #truncate the names of the columns so that they fit on the graph better
    trunc_features = [name[:-5] for name in df.columns]
    
    #create a new dataframe from these components
    df = pd.DataFrame(data=V, index=names, columns=trunc_features)
    
    #visualize only top n components:
    df = df.ix[0:components,:]
    
    #we'll only plot the components with the highest variance
    vars = df.var(axis=0)
    
    #sort them
    vars = vars.sort_values(ascending=False).index[0:features]
    df = df[vars]
    df['components']= df.index
    pd.tools.plotting.parallel_coordinates(df,'components');  

def plotComponentFeatures(df,ind=0):
    '''Ingests a normalized dataframe and component index and returns a plot 
    of feature weights that comprise the component'''
    # set larger font
    sns.set(font_scale=1.5)
    # set figure size
    plt.rcParams['figure.figsize']=(20,5)
    U, s, V = np.linalg.svd(df, full_matrices=False)
    #remove redundant characters from column name
    trunc_features = [name[:-5] for name in df.columns]
    
    #might want to try the absolute value of the weights
    p = sns.barplot(x= trunc_features, y =  np.abs(V[ind])) 
    
    #rotate axis labels by 90 deg
    p.set_xticklabels(p.get_xticklabels(), rotation=90)
    
    #lable the graph
    p.set(xlabel='Features', ylabel='Weight')
    
    # Add a title
    sns.plt.title('Features Weights for Component');


def findSimilar(ind,df,n=5,axis=0):
    '''ingests a dataframe and an index of either a feature or row in the dataframe, as well as a desired number 
    of similar products/features, with corresponding axis set to 0/1 to describe whether row or column is the desired
    output'''
    U, s, V = np.linalg.svd(df, full_matrices=False)
    #if we want products, we will use U
    if axis==0:
        X = U
    #if we want features, we will use V
    else:
        X = V
        
    food = X[ind]    
    loc = np.argsort(np.concatenate(np.delete(cosine_similarity(X,food),ind,0)))[::-1]
    loc = np.array([i+1 if i >= ind else i for i in loc])
    #returns the top y products similar to the one you picked
    if axis==0:
        print("For product {}, similar products are: {}".format(df.index[ind],[df.index[i] for i in loc[0:n]]))
    else:
        print("For nutrient {}, similar nutrients are: {}".format(df.columns[ind],[df.columns[i] for i in loc[0:n]]))

def designSimilarProduct(imaginary_product_array,df,n=5):
    U, s, V = np.linalg.svd(df, full_matrices=False)
           
    food = imaginary_product_array.dot(V.T).dot((np.linalg.inv(np.diag(s))))   
    loc = np.argsort(np.concatenate(cosine_similarity(U,food)))[::-1]
    #returns the top y products similar to the one you picked

    return [df.index[i] for i in loc[0:n]]

def SVDLinRegCoef(df,y):
    '''takes in a dataframe,which contains the independent variables 
    and an array which contains the dependent variables'''
    # once more, we take do SVD
    U, s, V = np.linalg.svd(df, full_matrices=False)
    
    s_inv = np.linalg.inv(np.diag(s))
    
    # quality check to assure that y is the forma that we want
    y = np.array(y)
    
    # now we can apply the formula from the paper. The key is that S is actually going to be it's inverse rather
    # than just multiplying out USV
    return V.T.dot(s_inv.dot(U.T.dot(y)))

def SVDLinRegPredict(df,coef):
    '''once we ran SVDLinRegCoef, we would ideally like to be able to use the coefficients to our advantage
    to generate predictions'''
    #convert df to a matrix
    m = df.values
    
    #set our counter to 0
    predicts = 0
    
    #iterate over our features
    for i in range(len(coef)):
        #sum up the betas * the inputs 
        predicts += coef[i]*m.T[i] 
        
    #return our predictions    
    return predicts    

def OutputFoodGroups(df,groups=10,products=10):
    '''Ingest a dataframe, the number of food groups desired, and how many foods to include in each group. 
    Outputs a list of products corresponding to each component'''
    U, s, V = np.linalg.svd(df, full_matrices=False)
    #select the first columns corresponding to the number of components
    #and take the absolute value of their eigenvecters and sort them
    sorted_U_loc= [np.argsort(np.abs(x)) for x in U.T[0:groups]]
    #reverse the sorting order
    sorted_U_loc = sorted_U_loc[::-1]
    #pick out the products you want
    products = np.array(df.index)
    #returns a list of each food group
    return [[products[j] for j in sorted_U_loc[i][0:products]] for i in range(groups)]    



