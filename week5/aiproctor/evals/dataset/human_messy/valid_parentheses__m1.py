def is_valid(s):
    st=[]
    for c in s:
        if c=='(' or c=='[' or c=='{':
            st.append(c)
        else:
            if len(st)==0:
                return False
            t=st.pop()
            if c==')' and t!='(': return False
            if c==']' and t!='[': return False
            if c=='}' and t!='{': return False
    return len(st)==0


s = input().strip()
print("true" if is_valid(s) else "false")
